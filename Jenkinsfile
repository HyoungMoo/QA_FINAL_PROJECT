pipeline {
    agent any

    environment {
        PYTHONIOENCODING = 'utf-8'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'python -m pytest part1_api_automation/tests/ -m p0 --html=report.html --self-contained-html -v'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report.html', allowEmptyArchive: true
        }
        success {
            echo 'Tests passed!'
        }
        failure {
            echo 'Tests failed!'
        }
    }
}
