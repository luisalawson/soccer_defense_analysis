import { Octokit } from "@octokit/core";
import fs from 'fs';
import path from 'path';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.GITHUB_REPOSITORY?.split('/')[1];
const OWNER = process.env.GITHUB_REPOSITORY?.split('/')[0];
const PR_NUMBER = process.env.PR_NUMBER;

if (!GITHUB_TOKEN || !REPO || !OWNER || !PR_NUMBER) {
    console.error("Missing required environment variables.");
    process.exit(1);
} 
// Getting changed files in the pull request
async function getFiles(){
    const octokit = new Octokit({
        auth: GITHUB_TOKEN
    })
    const files = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}/files', {
        owner: OWNER,
        repo: REPO,
        pull_number: PR_NUMBER,
        headers: {
        'X-GitHub-Api-Version': '2022-11-28'
        }
    })
    return files.data.map(file => file.filename);
}
// Analizing files for internal word
function searchInternalKeyword(changedFiles) {
    // we only care for ts or js files here
    relevantFiles = changedFiles.filter(file => file.endsWith('.ts') || file.endsWith('.js'));
    let internalEndpoints = [];
    relevantFiles.forEach(filePath => {
        try {
            const absolutePath = path.resolve(filePath); 
            console.log(`Processing file: ${absolutePath}`);
            const content = fs.readFileSync(absolutePath, 'utf-8'); 
            const combinedExp = /internal\/[^?'`"]*[?'`"]/g;
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

// Analizing files for tokens
function searchTokens(changedFiles) {
    let dangerFiles = [];
    const regexList = [
        // https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml
        // jwt token
        /\b(ey[a-zA-Z0-9]{17,}\.ey[a-zA-Z0-9\/\\_-]{17,}\.(?:[a-zA-Z0-9\/\\_-]{10,}={0,2})?)(?:['|\"|\n|\r|\s|\x60|;]|$)/g,
        // jwt base64 token
        /\bZXlK(?:(aGJHY2lPaU)|(aGNIVWlPaU)|(aGNIWWlPaU)|(aGRXUWlPaU)|(aU5qUWlP)|(amNtbDBJanBi)|(amRIa2lPaU)|(bGNHc2lPbn)|(bGJtTWlPaU)|(cWEzVWlPaU)|(cWQyc2lPb)|(cGMzTWlPaU)|(cGRpSTZJ)|(cmFXUWlP)|(clpYbGZiM0J6SWpwY)|(cmRIa2lPaUp)|(dWIyNWpaU0k2)|(d01tTWlP)|(d01uTWlPaU)|(d2NIUWlPaU)|(emRXSWlPaU)|(emRuUWlP)|(MFlXY2lPaU)|(MGVYQWlPaUp)|(MWNtd2l)|(MWMyVWlPaUp)|(MlpYSWlPaU)|(MlpYSnphVzl1SWpv)|(NElqb2)|(NE5XTWlP)|(NE5YUWlPaU)|(NE5YUWpVekkxTmlJNkl)|(NE5YVWlPaU)|(NmFYQWlPaU))[a-zA-Z0-9\/\\_+\-\r\n]{40,}={0,2}/g
    ];
    changedFiles.forEach(filePath => {
        try {
            const absolutePath = path.resolve(filePath);
            const content = fs.readFileSync(absolutePath, 'utf-8');
            regexList.forEach(regex => {
                const matches = content.match(regex);
                if (matches) {
                    dangerFiles.push(filePath);
                }
            });
        } catch (error) {
            console.error(`Error reading file ${filePath}:`, error);
        }
    });
    return dangerFiles;
}

// Posting the comment in the PR - internal endpoints
async function postCommentInternal(endpoints) {
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

// Posting the comment in the PR - tokens
async function postCommentTokens(files) {
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    let commentBody = `Hey! There are potential tokens on the following files:\n`;
    files.forEach((filepath) => {
        commentBody += `- ${filepath}\n`;
    });
    commentBody += `\nPlease make sure no hardcoded tokens are present in the snap-in.`;
    await octokit.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
        owner: OWNER,
        repo: REPO,
        issue_number: PR_NUMBER,
        body: commentBody,
        headers: { 'X-GitHub-Api-Version': '2022-11-28' }
    });
}

// Main function
async function main() {
    try {
        const files = await getFiles();
        
        const internalEndpoints = searchInternalKeyword(files);
        const conflictFiles = searchTokens(files);

        if (internalEndpoints.length > 0 && conflictFiles.length > 0) {
            await postCommentInternal(internalEndpoints);
            await postCommentTokens(internalEndpoints);
            process.exit(1);
        } else if(internalEndpoints.length > 0 && conflictFiles.length == 0) {
            await postCommentInternal(internalEndpoints);
            process.exit(1);
        } else if(internalEndpoints.length == 0 && conflictFiles.length > 0) {
            await postCommentTokens(conflictFiles);
            process.exit(1);
        } else {
            process.exit(0);
        }
    } catch (error) {
        console.error("Error in script execution:", error);
        process.exit(1);
    }
}
main();
