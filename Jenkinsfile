pipeline {
    // Указание агента, на котором будет выполняться pipeline
    agent any

    // Определение переменных окружения
    environment {
        // Путь к репозиторию
        REPO_URL = 'https://github.com/ig-rudenko/taged'
        VENV_NAME = 'venv'
    }

    // Определение шагов pipeline
    stages {
        // Стадия копирования репозитория
        stage('Clone repo') {
            steps {
                // Клонирование репозитория с помощью git
                git url: "${REPO_URL}"
            }
        }

        // Стадия создания виртуального окружения Python и установки зависимостей
        stage('Setup Python environment') {
            steps {
                // Создание виртуального окружения Python с помощью virtualenv
                sh "python3 -m venv ${VENV_NAME}"
                // Активация виртуального окружения
                sh '''#!/bin/bash
                    source ${VENV_NAME}/bin/activate
                    pip install -r requirements.txt && pip install coverage'''
            }
        }

        // Стадия запуска тестов и генерации отчета coverage.py
        stage('Run tests and coverage') {
            steps {
                // Запуск тестов и генерации отчета coverage.py с помощью coverage
                sh '''#!/bin/bash
                    source ${VENV_NAME}/bin/activate
                    export DJANGO_DEBUG=1
                    coverage run --source='.' manage.py test && coverage html'''
            }
        }

        // Стадия публикации HTML-отчета coverage
        stage('Publish coverage report') {
            steps {
                // Публикация HTML-отчета с помощью плагина HTML Publisher
                publishHTML (target: [
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'htmlcov',
                    reportFiles: 'index.html',
                    reportName: 'Coverage Report',
                ])
            }
        }

        // Стадия запуска ansible-playbook из папки проекта "ansible"
        stage('Deploy with Ansible') {
            steps {
                configFileProvider([configFile(fileId: 'knowledge-base-ansible-hosts-file', variable: 'HOSTS_FILE')]) {
                    ansiColor('xterm') {
                        ansiblePlaybook (
                            installation: 'Ansible', // Имя установки Ansible из Global Tool Configuration
                            playbook: 'ansible/playbooks/deploy.yaml', // Путь к playbook в папке проекта "ansible"
                            inventory: "${HOSTS_FILE}", // Путь к файлу hosts, который хранится в jenkins configuration manager
                            disableHostKeyChecking: true, // Отключение проверки ключа хоста SSH для избежания ошибок подключения
                            colorized: true, // Включение цветного вывода для лучшей читаемости
                        )
                    }
                }
            }
        }

    }

    // Post-секция выполняется независимо от результата стадий основного пайплайна
    post {
        success {
            withCredentials([string(credentialsId: 'tg_notification_bot_token', variable: 'TOKEN'), string(credentialsId: 'tg_notification_chat_id', variable: 'CHAT_ID')]) {
            sh  ("""
            curl -s -X POST https://api.telegram.org/bot${TOKEN}/sendMessage \
            -d chat_id=${CHAT_ID} \
            -d parse_mode=markdown \
            -d text='✅ *${env.JOB_NAME}* \n*Deployment* : OK \n*Git branch*: ${env.GIT_BRANCH}\n*Сборка*: ${BUILD_NUMBER}\n\n${REPO_URL}/commit/${env.GIT_COMMIT}'
            """)
            }
        }

        aborted {
            withCredentials([string(credentialsId: 'tg_notification_bot_token', variable: 'TOKEN'), string(credentialsId: 'tg_notification_chat_id', variable: 'CHAT_ID')]) {
            sh  ("""
            curl -s -X POST https://api.telegram.org/bot${TOKEN}/sendMessage \
            -d chat_id=${CHAT_ID} \
            -d parse_mode=markdown \
            -d text='⛔️ *${env.JOB_NAME}* \n*Deployment* : Aborted \n*Git branch*: ${env.GIT_BRANCH}\n*Сборка* ${BUILD_NUMBER}\n\n${REPO_URL}/commit/${env.GIT_COMMIT}'
            """)
            }
        }

        failure {
            withCredentials([string(credentialsId: 'tg_notification_bot_token', variable: 'TOKEN'), string(credentialsId: 'tg_notification_chat_id', variable: 'CHAT_ID')]) {
            sh  ("""
            curl -s -X POST https://api.telegram.org/bot${TOKEN}/sendMessage \
            -d chat_id=${CHAT_ID} \
            -d parse_mode=markdown \
            -d text='❌ *${env.JOB_NAME}* \n*Deployment* : Failed\n*Git branch*: ${env.GIT_BRANCH}\n*Сборка* ${BUILD_NUMBER}\n\n${REPO_URL}/commit/${env.GIT_COMMIT}'
            """)
            }
        }

    }

}