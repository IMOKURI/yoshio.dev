workflow "Deploy on Push" {
  on = "push"
  resolves = ["GitHub Action for Google Cloud"]
}

action "Setup Google Cloud" {
  uses = "actions/gcloud/auth@master"
  secrets = ["GCLOUD_AUTH"]
}

action "GitHub Action for Google Cloud" {
  uses = "actions/gcloud/cli@master"
  needs = ["Setup Google Cloud"]
  runs = "bash -c"
  args = ["echo 'hello' > /tmp/github_actions.txt"]
}
