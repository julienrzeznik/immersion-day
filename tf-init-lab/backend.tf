terraform {
  backend "gcs" {
    bucket = "immersion-day-central-hub-008-tfstate"
    prefix = "terraform/state"
  }
}
