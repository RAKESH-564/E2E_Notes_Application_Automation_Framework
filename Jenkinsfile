pipeline {

    agent {
        label 'windows'
    }

    environment {

        HEADLESS = 'true'

        REMOTE = 'false'
    }

    stages {

        stage('Checkout Code') {

            steps {

                checkout scm

                echo 'Code downloaded successfully'
            }
        }

        // stage('Start Selenium Grid') {

        //     steps {

        //         bat '''
        //             docker-compose up -d
        //         '''
        //     }
        // }

        stage('Install Dependencies') {

            steps {

                bat '''
                    python -m venv .venv

                    call .venv\\Scripts\\activate

                    python -m pip install --upgrade pip

                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run API Tests') {

            steps {
                
                catchError(
                    buildResult: 'SUCCESS',
                    stageResult: 'FAILURE'
                ) {

                bat '''
                    call .venv\\Scripts\\activate

                    pytest tests/test_api_notes.py -v --alluredir=reports/allure-results
                '''
                }
            }

        }

        stage('Run UI Login Tests') {

            steps {

                bat '''
                    call .venv\\Scripts\\activate

                    pytest tests/test_login.py -v --alluredir=reports/allure-results
                '''
            }
        }

        stage('Run UI Notes Tests') {

            steps {

                bat '''
                    call .venv\\Scripts\\activate

                    pytest tests/test_product.py -v --alluredir=reports/allure-results
                '''
            }
        }

        stage('Run E2E Tests') {

            steps {

                bat '''
                    call .venv\\Scripts\\activate

                    pytest tests/test_e2e_hybrid.py -v --alluredir=reports/allure-results
                '''
            }
        }

        stage('Generate Allure Report') {

            steps {

                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'reports/allure-results']]
                ])
            }
        }

        stage('Archive Reports') {

            steps {

                archiveArtifacts artifacts: 'reports/**/*', fingerprint: true

                echo 'Reports archived successfully'
            }
        }
    }

    post {

        always {

            // bat '''
            //     docker-compose down
            // '''

            echo 'Pipeline execution completed'
        }

        success {

            echo 'Build completed successfully'
        }

        failure {

            echo 'Build failed'
        }
    }
}
