terraform {
  required_providers {
    github = {
      source  = "integrations/github"
      version = "~> 6.0" # Rulesets require a relatively new provider version
    }
  }
}

# Configure the GitHub Provider
provider "github" {
  owner = "skurekjakub" 
  # We will pass the token via an environment variable for security
}

# Your original snippet
resource "github_repository_ruleset" "main_protection" {
  name        = "Golden Standard Protection"
  repository  = "knowledge-rag" # <--- MAKE SURE THIS REPO EXISTS ALREADY
  target      = "branch"
  enforcement = "active"

  bypass_actors {
    actor_id    = 5                # "5" is the GitHub ID for the "Repository Admin" role
    actor_type  = "RepositoryRole"
    bypass_mode = "always"
  }

  conditions {
    ref_name {
      include = ["~DEFAULT_BRANCH"]
      exclude = []
    }
  }

  rules {
    creation                = true
    deletion                = true
    non_fast_forward        = true # Updated property name (formerly 'update')
    
    required_linear_history = true
    
    pull_request {
      required_approving_review_count = 1
      dismiss_stale_reviews_on_push   = true
      require_code_owner_review       = true
      require_last_push_approval      = false
      required_review_thread_resolution = true
    }
  }
}