import { Octokit } from "@octokit/core";

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
    const addedFiles = files.data.filter(file => file.status === "added").map(file => file.filename);
    const modifiedFiles = files.data.filter(file => file.status === "modified" || file.status === "changed").map(file => file.filename);
    return addedFiles, modifiedFiles;

}

async function postComment(folderName) {
    const octokit = new Octokit({ auth: GITHUB_TOKEN });
    let commentBody = `Please update the CODEOWNERS file with the following line:\n `;
    commentBody += `* /${folderName}/  @${OWNER}  @devrev-aai-reviewers \n\n`;
    commentBody += `👀 ONLY ADD **@devrev-aai-reviewers** IF YOU ARE A MEMBER OF AAI ENGINEERS`;
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
        const [addedFiles, modifiedFiles] = await getFiles();
        console.log("Added files: ", addedFiles);
        console.log("Modified files: ", modifiedFiles);
        // no added files found, no snap-in created
        if(addedFiles === undefined){
            console.log("No files were added. Skipping CODEOWNERS check.");
            process.exit(0);
        }
        // if there are more than 20 files added, we assume the PR is for a snap-in
        if (addedFiles.length < 20) {
            console.log("Less than 20 files were added. Assuming no new snap-in created. Skipping CODEOWNERS check.");
            process.exit(0);
        }
        let codeowners = false;
        // if there are any modified files, check if CODEOWNERS file is modified
        if (modifiedFiles !== undefined) {
            codeowners = modifiedFiles.find(file => file === '.github/CODEOWNERS');
        } else {
            codeowners = false;
        }
        if(codeowners){
            process.exit(0);
        }
        const folders = addedFiles.map((file) => file.split("/")[0]);
        const folderNames = [...new Set(folders)];
        let snapInName = '';
        if (folderNames.length > 1) {
            console.log("Multiple folders modified in the PR. Assuming no new snap-in created.");
            process.exit(0);
        } else {
            snapInName = folderNames[0];
        }
        await postComment(snapInName);
        process.exit(1);
    } catch (error) {
        console.error("Error in script execution:", error);
        process.exit(1);
    }
}

main();