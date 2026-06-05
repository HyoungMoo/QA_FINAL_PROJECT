pipeline {
    agent any

    environment {
        PYTHONIOENCODING = 'utf-8'
        PYTHON = 'C:\\Users\\khm40\\AppData\\Local\\Programs\\Python\\Python38-32\\python.exe'
        ENV_FILE = 'C:\\Users\\khm40\\OneDrive\\바탕 화면\\qa_final_project\\elice_lxp_test_team3\\.env'
    }

    stages {
        stage('Install Dependencies') {
            steps {
                bat '"%PYTHON%" -m pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'copy "%ENV_FILE%" .env'
                bat '"%PYTHON%" -m pytest part1_api_automation/tests/ -m p0 --html=report.html --self-contained-html -v'
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
