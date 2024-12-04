import { Octokit } from "@octokit/core";
import fs from 'fs';
import path from 'path';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.GITHUB_REPOSITORY?.split('/')[1];
const OWNER = process.env.GITHUB_REPOSITORY?.split('/')[0];
const PR_NUMBER = process.env.PR_NUMBER;
const FILES = process.env.FILES?.split(/\s+/).filter(Boolean); // Split and clean the FILES list

if (!GITHUB_TOKEN || !REPO || !OWNER || !PR_NUMBER || !FILES) {
    console.error("Missing required environment variables.");
    process.exit(1);
}

function searchInternalKeyword(changedFiles) {
    let internalEndpoints = new Map();

    changedFiles.forEach(filePath => {
        try {
            const content = fs.readFileSync(filePath, 'utf-8');
            const internalExp = /'\/internal\/[^']+'/g;
            const endpointsFound = content.match(internalExp);

            if (endpointsFound) {
                internalEndpoints.set(filePath, endpointsFound);
            }
        } catch (error) {
            console.error(`Error reading file ${filePath}:`, error);
        }
    });

    return Array.from(internalEndpoints);
}

async function postComment(endpoints) {
    const octokit = new Octokit({ auth: GITHUB_TOKEN });

    if (endpoints.length > 0) {
        let commentBody = `Please explain why you are using the following internal endpoints:\n`;
        endpoints.forEach(([filePath, endpointList]) => {
            commentBody += `- ${filePath}:\n`;
            endpointList.forEach(endpoint => {
                commentBody += `  - ${endpoint}\n`;
            });
        });

        await octokit.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
            owner: OWNER,
            repo: REPO,
            issue_number: PR_NUMBER,
            body: commentBody,
            headers: { 'X-GitHub-Api-Version': '2022-11-28' }
        });
    } else {
        await octokit.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
            owner: OWNER,
            repo: REPO,
            issue_number: PR_NUMBER,
            body: 'Great job! No internal endpoints were found in the changed files 🚀',
            headers: { 'X-GitHub-Api-Version': '2022-11-28' }
        });
    }
}

async function main() {
    try {
        const internalEndpoints = searchInternalKeyword(FILES);

        if (internalEndpoints.length > 0) {
            await postComment(internalEndpoints);
        } else {
            console.log("No internal endpoints detected.");
        }
    } catch (error) {
        console.error("Error in script execution:", error);
        process.exit(1);
    }
}

main();

