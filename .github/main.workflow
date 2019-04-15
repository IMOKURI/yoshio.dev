workflow "Deploy on Push" {
  on = "push"
  resolves = ["GitHub Action for Google Cloud"]
}

action "Deploy only master branch" {
  uses = "actions/bin/filter@master"
  args = "branch master"
}

action "Setup Google Cloud" {
  uses = "actions/gcloud/auth@master"
  needs = ["Deploy only master branch"]
  secrets = ["GCLOUD_AUTH"]
}

action "GitHub Action for Google Cloud" {
  uses = "actions/gcloud/cli@master"
  needs = ["Setup Google Cloud"]
  args = ["compute", "copy-files", "--project", "steady-petal-233414", "--zone", "us-west1-b", ".", "yoshio-vm001:/tmp/github_actions"]
}
