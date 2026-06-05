pipeline {
    agent any

    environment {
        PYTHONIOENCODING = 'utf-8'
        PYTHON = 'c:\\Users\\khm40\\OneDrive\\바탕 화면\\qa_final_project\\venv\\Scripts\\python.exe'
        ENV_FILE = 'C:\\jenkins_config\\.env'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                powershell 'Copy-Item $env:ENV_FILE -Destination ".env"'
                bat '"%PYTHON%" -m pytest part1_api_automation/tests/ --html=report.html --self-contained-html -v'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'report.html', allowEmptyArchive: true
        }
        success {
            echo 'All tests passed!'
        }
        failure {
            echo 'Some tests failed!'
        }
    }
}
