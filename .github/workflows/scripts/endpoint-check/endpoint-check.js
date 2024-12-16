import { Octokit } from "@octokit/core";
import fs from 'fs';
import path from 'path';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.GITHUB_REPOSITORY?.split('/')[1];
const OWNER = process.env.GITHUB_REPOSITORY?.split('/')[0];
const PR_NUMBER = process.env.PR_NUMBER;
const FILES = process.env.FILES?.split(',').filter(Boolean); 

if (!GITHUB_TOKEN || !REPO || !OWNER || !PR_NUMBER) {
    console.error("Missing required environment variables.");
    process.exit(1);
} 
//internal/accounts.list?id=18181'
function searchInternalKeyword(changedFiles) {
    let internalEndpoints = [];
    
    changedFiles.forEach(filePath => {
        try {
            const absolutePath = path.resolve(filePath); 
            console.log(`Processing file: ${absolutePath}`);
            const content = fs.readFileSync(absolutePath, 'utf-8'); 
            const combinedExp = /internal\/[^'`]*['`?]/g;
            const endpointsFound = content.match(combinedExp);
            if (endpointsFound) {
                const uniqueEndpoints = Array.from(new Set(endpointsFound));
                internalEndpoints.push([filePath, uniqueEndpoints]);
            }
        } catch (error) {
            console.error(`Error reading file ${filePath}:`, error);
        }
    });
    return internalEndpoints;
}
//      `${endpoint}/internal/recommendations.chat.completions`,

async function postComment(endpoints) {
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    let commentBody = `Hey! I noticed you are using the following internal endpoints:\n`;
    endpoints.forEach(([filePath, endpointList]) => {
        commentBody += `- ${filePath}:\n`;
        endpointList.forEach(endpoint => {
            commentBody += `  - ${endpoint}\n`;
        });
    });
    commentBody += `\nInternal endpoints shouldn't be used, please follow the steps on this document: https://docs.google.com/document/d/1AMwAvWqhR-6HYIF32iB2Ecjv3IfqqoQSXX1ObzcOk8E/edit?usp=sharing`;
    await octokit.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
        owner: OWNER,
        repo: REPO,
        issue_number: PR_NUMBER,
        body: commentBody,
        headers: { 'X-GitHub-Api-Version': '2022-11-28' }
    });
}

async function main() {
    try {
        const internalEndpoints = searchInternalKeyword(FILES);
        if (internalEndpoints.length > 0) {
            await postComment(internalEndpoints);
            process.exit(1);
        } else {
            console.log("No internal endpoints found");
            process.exit(0);
        }
    } catch (error) {
        console.error("Error in script execution:", error);
        process.exit(1);
    }
}

main();
