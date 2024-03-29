terraform {
    required_providers {
        yandex = {
            source = "yandex-cloud/yandex"
        }
        docker = {
            source = "kreuzwerker/docker"
            // version = "~> 3.0.1"
        }
    }

    required_version = ">= 0.13"
}
