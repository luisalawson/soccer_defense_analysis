import { Octokit } from "@octokit/core";

// Environment variables
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY;
const PR_OWNER = process.env.PR_OWNER;
const PR_NUMBER = process.env.PR_NUMBER;

const [owner, repo] = GITHUB_REPOSITORY.split("/");

// Initialize Octokit
const octokit = new Octokit({ auth: GITHUB_TOKEN });

// File to update
const filePath = "CODEOWNERS";
const commitMessage = `Update CODEOWNERS with folder details from PR #${PR_NUMBER}`;

async function updateFile() {
  try {
    // Get the files changed in the PR
    const changedFiles = await octokit.request('GET /repos/{owner}/{repo}/pulls/{pull_number}/files', {
      owner,
      repo,
      pull_number: PR_NUMBER,
    });

    // Extract the folder name from the first changed file
    const folderName = changedFiles.data[0].filename.split("/")[0];
    console.log(`Folder added: ${folderName}`);

    // Fetch the current CODEOWNERS file
    let existingContent = "";
    let sha;

    try {
      const { data } = await octokit.request("GET /repos/{owner}/{repo}/contents/{path}", {
        owner,
        repo,
        path: filePath,
      });
      existingContent = Buffer.from(data.content, "base64").toString("utf-8");
      sha = data.sha;
    } catch (error) {
      if (error.status !== 404) throw error; // Handle non-404 errors
      console.log("CODEOWNERS file does not exist. Creating a new one.");
    }

    // Add the new entry to the CODEOWNERS file
    const newEntry = `/${folderName} @${PR_OWNER}`;
    const updatedContent = `${existingContent}\n${newEntry}`.trim();

    // Encode the updated content in Base64
    const encodedContent = Buffer.from(updatedContent).toString("base64");

    // Update or create the CODEOWNERS file
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
      sha, // Include `sha` only if updating an existing file
    });

    console.log("CODEOWNERS file updated successfully.");
  } catch (error) {
    console.error("Failed to update the CODEOWNERS file:", error.message);
    console.error("Stack trace:", error.stack);
    process.exit(1);
  }
}

// Run the function
updateFile();

