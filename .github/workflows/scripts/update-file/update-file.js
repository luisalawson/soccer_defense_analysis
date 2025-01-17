import { Octokit } from "@octokit/core";

// Environment variables
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY;
const PR_OWNER = process.env.PR_OWNER;
const PR_NUMBER = process.env.PR_NUMBER;

const [owner, repo] = GITHUB_REPOSITORY.split("/");

// Initialize Octokit since we'll be using Gitbub API
const octokit = new Octokit({ auth: GITHUB_TOKEN });

// File to update
const filePath = "CODEOWNERS";
const commitMessage = `Update CODEOWNERS with folder details from PR #${PR_NUMBER}`;

async function updateFile() {
  try {
    // Get the files changed in the PR -- we assume the files changed should have the name of the snap-in as the folder name
    const changedFiles = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}/files', {
      owner,
      repo,
      pull_number: PR_NUMBER,
    });

    // Extract the folder name from the first changed file 
    const folderName = changedFiles.data[0].filename.split("/")[0];

    // If more than 2 folders were changed, we return assuming the pr was to update general items for existing snap-ins
    if (changedFiles.data.length > 2) {
      console.log("More than 2 folders were changed. Skipping CODEOWNERS update.");
      return;
    }
    console.log(`Folder added: ${folderName}`);

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
      // Decode the content from Base64 (github actions) to UTF-8 
      existingContent = Buffer.from(data.content, "base64").toString("utf-8");
      sha = data.sha;
    } catch (error) {
      if (error.status !== 404) throw error; 
      console.log("CODEOWNERS file does not exist. Creating a new one.");
    }

    // check if the folder added is already present in the CODEOWNERS file 
    const folderPresent = existingContent.includes(`/${folderName}`);
    if (folderPresent) {
      console.log(`Snap-in ${folderName} already exists in CODEOWNERS file.`);
      // Assuming the owner should be one, if the folder exists, we won't update the CODEOWNERS file
      process.exit(0);
    }

    // Add the new entry to the CODEOWNERS file
    const newEntry = `/${folderName}/ @${PR_OWNER}`;
    const updatedContent = `${existingContent}\n${newEntry}`.trim();

    // Encode the updated content in Base64 -- required for the Github API
    const encodedContent = Buffer.from(updatedContent).toString("base64");

    // Update or create the CODEOWNERS file - https://docs.github.com/en/rest/repos/contents?apiVersion=2022-11-28#create-or-update-file-contents 
    await octokit.request("PUT /repos/{owner}/{repo}/contents/{path}", {
      owner,
      repo,
      path: filePath,
      message: commitMessage,
      committer: {
        name: "GitHub Actions",
        email: "actions@github.com",
      },
      content: encodedContent,
      sha, // Include `sha` since we are updating an existing file
    });
    console.log("CODEOWNERS file updated successfully.");
    process.exit(0);
  } catch (error) {
    console.error("Failed to update the CODEOWNERS file:", error.message);
    process.exit(1);
  }
}

updateFile();
