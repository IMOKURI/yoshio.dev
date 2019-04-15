workflow "Deploy on Push" {
  on = "push"
  resolves = ["Release Source on GCP"]
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

action "Clear Work Directory on GCP" {
  uses = "actions/gcloud/cli@master"
  needs = ["Setup Google Cloud"]
  args = ["compute", "ssh", "yoshio@yoshio-vm001", "--project=steady-petal-233414", "--zone=us-west1-b", "--", "rm", "-rf", "/tmp/github_actions"]
}

action "Create Work Directory on GCP" {
  uses = "actions/gcloud/cli@master"
  needs = ["Clear Work Directory on GCP"]
  args = ["compute", "ssh", "yoshio@yoshio-vm001", "--project=steady-petal-233414", "--zone=us-west1-b", "--", "mkdir", "-p", "/tmp/github_actions"]
}

action "Upload Source to GCP" {
  uses = "actions/gcloud/cli@master"
  needs = ["Create Work Directory on GCP"]
  args = ["compute", "scp", "--project=steady-petal-233414", "--zone=us-west1-b", "--recurse", ".", "yoshio@yoshio-vm001:/tmp/github_actions"]
}

action "Release Source on GCP" {
  uses = "actions/gcloud/cli@master"
  needs = ["Upload Source to GCP"]
  args = ["compute", "ssh", "yoshio@yoshio-vm001", "--project=steady-petal-233414", "--zone=us-west1-b", "--", "bash", "/tmp/github_actions/release.sh"]
}
