import { Octokit } from "@octokit/core";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY;
const PR_OWNER = process.env.PR_OWNER;
const PR_NUMBER = process.env.PR_NUMBER;

const [owner, repo] = GITHUB_REPOSITORY.split("/");

// Initialize Octokit since we'll be using GitHub API
const octokit = new Octokit({ auth: GITHUB_TOKEN });

// File to update
const filePath = ".github/CODEOWNERS";
const commitMessage = `Update CODEOWNERS with folder details from PR #${PR_NUMBER}`;
const branchName = `update-codeowners-${PR_NUMBER}`;

async function updateFile() {
  try {
    // Get the files changed in the PR -- we assume the files changed should have the name of the snap-in as the folder name
    const changedFiles = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}/files', {
      owner,
      repo,
      pull_number: PR_NUMBER,
    });

    // Extract the folder name from all the files changed
    const folderNames = changedFiles.data.map((file) => file.filename.split("/")[0]);
    // Get the unique folder names
    const uniqueFolderNames = [...new Set(folderNames)];

    // If more than 2 folders were changed, we return assuming the pr was to update general items for existing snap-ins
    if (uniqueFolderNames.length > 2) {
      console.log("More than 2 folders were changed. Skipping CODEOWNERS update.");
      return;
    }

    const uniqueFolder = uniqueFolderNames[0];
    
    console.log(`Folder added: ${uniqueFolder}`);

    // Fetch the current CODEOWNERS file -- we'll be modifying these variables
    let existingContent = "";
    let sha;

    try {
      // Get the file of CODEOWNERS to add the content we want -- https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#get-repository-content 
      const { data } = await octokit.request("GET /repos/{owner}/{repo}/contents/{path}", {
        owner,
        repo,
        // The path to the file since we don't want all the files in the repository
        path: filePath,
      });
      // Decode the content from Base64 (gh actions) to UTF-8 
      existingContent = Buffer.from(data.content, "base64").toString("utf-8");
      sha = data.sha;
    } catch (error) {
      if (error.status !== 404) throw error; 
      console.log("CODEOWNERS file does not exist. Creating a new one.");
    }

    // check if the folder added is already present in the CODEOWNERS file 
    const folderPresent = existingContent.includes(`/${uniqueFolder}`);
    if (folderPresent) {
      console.log(`Snap-in ${uniqueFolder} already exists in CODEOWNERS file.`);
      // Assuming the owner should be one, if the folder exists, we won't update the CODEOWNERS file
      process.exit(0);
    }

    // Add the new entry to the CODEOWNERS file
    const newEntry = `/${uniqueFolder}/ @${PR_OWNER}`;
    const updatedContent = `${existingContent}\n${newEntry}`.trim();

    // Encode the updated content in Base64 -- required for the Github API
    const encodedContent = Buffer.from(updatedContent).toString("base64");

    // Create a new branch
    await octokit.request("POST /repos/{owner}/{repo}/git/refs", {
      owner,
      repo,
      ref: `refs/heads/${branchName}`,
      sha: (await octokit.request("GET /repos/{owner}/{repo}/git/refs/heads/main", { owner, repo })).data.object.sha,
    });

    // Update the CODEOWNERS file on the new branch
    await octokit.request("PUT /repos/{owner}/{repo}/contents/{path}", {
      owner,
      repo,
      path: filePath,
      message: commitMessage,
      content: encodedContent,
      branch: branchName,
      sha, // Include sha since we are updating an existing file
    });

    // Create a pull request
    await octokit.request("POST /repos/{owner}/{repo}/pulls", {
      owner,
      repo,
      title: commitMessage,
      head: branchName,
      base: "main",
      body: `This PR updates the CODEOWNERS file with the folder details from PR #${PR_NUMBER}.`,
    });

    console.log("Pull request created successfully.");
    process.exit(0);
  } catch (error) {
    console.error("Failed to update the CODEOWNERS file and create a pull request:", error.message);
    process.exit(1);
  }
}

updateFile();
