import { Octokit } from "@octokit/core";
import fs from 'fs';
import path from 'path';

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO = process.env.GITHUB_REPOSITORY.split('/')[1];
const OWNER = process.env.GITHUB_REPOSITORY.split('/')[0];
const ISSUE_NUMBER = process.env.ISSUE_NUMBER;
const PR_NUMBER = process.env.PR_NUMBER;


async function getChangedFiles() {
    const filenames = []
    const octokit = new Octokit({
        auth: GITHUB_TOKEN
    })
    const response = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}/files', {
        owner: OWNER,
        repo: REPO,
        pull_number: PR_NUMBER,
        headers: {
        'X-GitHub-Api-Version': '2022-11-28'
        }
    })
    for (const file of response.data) {
        if(file.status === 'added' || file.status === 'modified'){
            filenames.push(file.filename);
        }
    }
    return filenames;
}
function searchInternalKeyword(changedFiles) {
    let internalEndpoints = new Map();
    function readFiles(directory) {
        const files = fs.readdirSync(directory);
        files.forEach(file => {
            const filePath = path.join(directory, file);
            const stat = fs.statSync(filePath);
            if (stat.isDirectory()) { 
                readFiles(filePath);
            } else if (file.endsWith('.ts') && changedFiles.includes(file)) {
                const content = fs.readFileSync(filePath, 'utf-8');
                // not internal only to avoid matching the internal keyword for timeline entry comments
                const internalExp = /'\/internal\/[^']+'/g;
                const endpointsFound = content.match(internalExp);
                if (endpointsFound) {
                    if (!internalEndpoints.has(filePath)) {
                        internalEndpoints.set(filePath, []);
                    }
                    endpointsFound.forEach(endpoint => internalEndpoints.get(filePath).push(endpoint));
                }
            }
        });
    }
    readFiles('.');
    return Array.from(internalEndpoints);
}

async function postComment(endpoints){
    let commentBody = `Please explain why you are using the following internal endpoints:\n`;
    endpoints.forEach(([filePath, endpoint]) => {
        commentBody += `- ${endpoint} in ${filePath}\n`;
    });
    // https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#create-an-issue-comment 
    // https://github.com/octokit/core.js#readme
    const octokit = new Octokit({
        auth: GITHUB_TOKEN
    })
    await octokit.request('POST /repos/{owner}/{repo}/issues/{issue_number}/comments', {
        owner: OWNER,
        repo: REPO,
        issue_number: PR_NUMBER,
        body: commentBody,
        headers: {
        'X-GitHub-Api-Version': '2022-11-28'
        }
    })
}

async function main() {
    // const changedFiles = await getChangedFiles();
    // const internalEndpoints = searchInternalKeyword(changedFiles);
    // if (internalEndpoints.length > 0) {
    //     await postComment(internalEndpoints);
    // }
    console.log(`issue number is ${ISSUE_NUMBER} and PR number is ${PR_NUMBER}`);
}

main();
