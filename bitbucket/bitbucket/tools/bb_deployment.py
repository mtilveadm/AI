from atlassian import Bitbucket
import logging
import os
from dotenv import load_dotenv

logger = logging.getLogger("BitbucketDeploymentTool")

load_dotenv()  # Loads variables from .env

class BitbucketDeploymentTool:
    def __init__(self, username: str, password: str, cloud: bool = True):
        self.client = Bitbucket(
            url="https://api.bitbucket.org/",
            username=username,
            password=password,
            cloud=cloud
        )

    def trigger_pipeline(self, repo_slug: str, workspace: str, branch: str = "master"):
        logger.info(f"Triggering pipeline for repo: {repo_slug}, workspace: {workspace}, branch: {branch}")
        try:
            result = self.client.trigger_pipeline(workspace=workspace, repo_slug=repo_slug, branch=branch)
            logger.info(f"Pipeline trigger result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error triggering pipeline: {e}")
            return f"Error triggering pipeline: {e}"
        

    def list_deployment_environments(self, repo_slug: str, workspace: str):
        logger.info(f"Listing deployment environments for repo: {repo_slug}, workspace: {workspace}")
        try:
            deployments = self.client.get_deployments(workspace=workspace, repo_slug=repo_slug)
            logger.info(f"Deployment environments: {deployments}")
            return deployments
        except Exception as e:
            logger.error(f"Error listing deployments: {e}")
            return f"Error listing deployments: {e}"

def deploy_pipeline_tool(repo_slug: str, workspace: str, branch: str = "master"):
    # Instantiate your BitbucketDeploymentTool here if needed
    tool = BitbucketDeploymentTool(
        username=os.getenv("BITBUCKET_USERNAME"),
        password=os.getenv("BITBUCKET_APP_PASSWORD"),
        username=os.getenv("BITBUCKET_WORKSPACE"),  
        cloud=True
    )
    return tool.trigger_pipeline(repo_slug=repo_slug, workspace=workspace, branch=branch)


def list_deployment_environments_tool(repo_slug: str, workspace: str):
    tool = BitbucketDeploymentTool(
        username=os.getenv("BITBUCKET_USERNAME"),
        password=os.getenv("BITBUCKET_APP_PASSWORD"),
        username=os.getenv("BITBUCKET_WORKSPACE"),
        cloud=True
    )
    return tool.list_deployment_environments(repo_slug=repo_slug, workspace=workspace)