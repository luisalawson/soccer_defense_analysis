import { Octokit } from "@octokit/core";
import fs from 'fs';
import path from 'path';

// Environment variables
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_REPOSITORY = process.env.GITHUB_REPOSITORY;
const PR_OWNER = process.env.PR_OWNER;
const PR_NUMBER = process.env.PR_NUMBER;

// Split owner and repo from the GITHUB_REPOSITORY env variable
const [owner, repo] = GITHUB_REPOSITORY.split("/");

// Initialize Octokit
const octokit = new Octokit({ auth: GITHUB_TOKEN });

// File to update
const filePath = "CODEOWNERS.txt";
const commitMessage = `Update file with details from PR #${PR_NUMBER}`;

// Main function
async function updateFile() {
  try {
    // Fetch the current file content (if it exists)
    let sha;
    let fileContent = `PR Merged by: ${PR_OWNER}\n`;

    try {
      const { data } = await octokit.request("GET /repos/{owner}/{repo}/contents/{path}", {
        owner,
        repo,
        path: filePath,
      });
      sha = data.sha;
      fileContent = Buffer.from(data.content, "base64").toString("utf-8") + fileContent;
    } catch (error) {
      if (error.status !== 404) throw error; // Ignore if file doesn't exist
    }

    // Append new details to the file content
    fileContent += `Details from PR #${PR_NUMBER}\n`;

    // Encode the content in Base64
    const encodedContent = Buffer.from(fileContent).toString("base64");

    // Update or create the file
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

    console.log("File updated successfully.");
  } catch (error) {
    console.error("Failed to update the file:", error);
    process.exit(1);
  }
}

// Run the function
updateFile();
