terraform {
  backend "gcs" {
    bucket = "immersion-day-central-hub-11-tfstate"
    prefix = "terraform/state"
  }
}
