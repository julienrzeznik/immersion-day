terraform {
  backend "gcs" {
    bucket = "immersion-day-central-hub-006-tfstate"
    prefix = "terraform/state"
  }
}
