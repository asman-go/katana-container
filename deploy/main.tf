// Собираем образ katana
resource "docker_image" "katana" {
  name = "cr.yandex/${var.container-repository}/katana:1.0"
}

// Загружаем образ в Docker Registry
resource "docker_registry_image" "helloworld" {
  name          = docker_image.katana.name
  keep_remotely = true
}
