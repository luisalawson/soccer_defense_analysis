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
    return files.data.filter(file => file.status !== "removed").map(file => file.filename);
}

async function postComment() {
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    let commentBody = `Please update the CODEOWNERS file with the following line:\n `;
    commentBody += `* /snap-in-name/  @${OWNER}  @devrev-ai-reviewers \n\n`;
    commentBody += `ONLY ADD **@devrev-ai-reviewers** IF YOU ARE A MEMBER OF AAI`;
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
        // if there are more than 20 files changed, we assume the PR is for a snap-in
        if (files.length < 1) {
            console.log("Less than 20 files were changed. Assuming no new snap-in created. Skipping CODEOWNERS check.");
            process.exit(0);
        }
        const codeowners = files.find(file => file === '.github/CODEOWNERS');
        const snapInName = files.find(file => file.includes('snap-ins'));
        if (!codeowners) {
            await postComment(snapInName);
            process.exit(1);
        }
        process.exit(0);
    } catch (error) {
        console.error("Error in script execution:", error);
        process.exit(1);
    }
}

main();
