workspace {
    name "MAI.DISK"
    description "Облачное хранилище"
    !adrs decisions
    !docs documentation
    !identifiers hierarchical

    model {
        user = person "Пользователь приложения"
        cloud_disk = softwareSystem "MAI.DISK"{
            description "Облачное хранилище данных"

            files_database = container "Files Database"{
                description "Хранит файлы по их ключам"
                technology "MongoDB"
            }

            user_database = container "User-Folders Database" {
                description "Хранит данные пользователей, доступы к папкам, ключи к файлам"
                technology "PostgreSQL 14"
            }

            files = container "Files" {
                -> files_database "Загружает, выгружает, удаляет файл из базы" "Spring Data MongoDB"
                technology "Java Spring"
            }

            folders = container "Folders" {
                -> user_database "Проверка доступов пользователя" "JDBC"
                -> files "Отправление запроса на взаимодействие с файлами" "API"
                technology "Java Spring"
            }
 
            frontend = container "Single Page Application"{
                -> folders "Передает запрос пользователя" "HTTPS"
                technology "REACT"
            }
        }
        user -> cloud_disk "Загружает файлы"
        user -> cloud_disk "Удаляет файлы"
        user -> cloud_disk "Выгружает файлы"
        user -> cloud_disk.frontend "Запрос на загрузку, выгрузку и удаление файлов"
    }

    views {
        themes default

        systemContext cloud_disk {
            include *
            autoLayout lr
        }
        
        container cloud_disk {
            include *
            autoLayout lr
        }

        dynamic cloud_disk {
            autoLayout lr
            user -> cloud_disk.frontend "Заходит на сайт"
            cloud_disk.frontend -> cloud_disk.folders "user_id"
            cloud_disk.folders -> cloud_disk.user_database "GET {user_id}/all_folders/all_files"

            user -> cloud_disk.frontend "Выбирает нужный файл"
            cloud_disk.frontend -> cloud_disk.folders "GET {user_id}/{folder}/{file_id}"
            cloud_disk.folders -> cloud_disk.user_database "verify"
            cloud_disk.folders -> cloud_disk.files "GET {file_id}"
            cloud_disk.files -> cloud_disk.files_database "Загружает нужный файл"
        }
    }

}