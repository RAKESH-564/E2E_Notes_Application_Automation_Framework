pipeline {

    agent {
        label 'windows'
    }

    environment {
        HEADLESS = 'true'
        REMOTE = 'false'
        LONGCAT_API_KEY = credentials('longcat-api-key')
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
                echo 'Code downloaded successfully'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                    if not exist .venv (
                        python -m venv .venv
                    )

                    call .venv\\Scripts\\activate

                    python -m pip install --upgrade pip

                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Clean Previous Allure Results') {
            steps {
                bat '''
                    if exist reports\\allure-results (
                        rmdir /s /q reports\\allure-results
                    )

                    if not exist reports (
                        mkdir reports
                    )

                    mkdir reports\\allure-results
                '''
            }
        }

        stage('Run API Tests') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    bat '''
                        call .venv\\Scripts\\activate

                        echo ==============================
                        echo RUNNING API TESTS
                        echo NO BROWSER REQUIRED
                        echo ==============================

                        python -m pytest tests/test_api_notes.py -v --alluredir=reports/allure-results
                    '''
                }
            }
        }

        stage('Run UI Login Tests') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    bat '''
                        call .venv\\Scripts\\activate

                        echo ==============================
                        echo RUNNING UI LOGIN TESTS
                        echo HEADLESS=%HEADLESS%
                        echo ==============================

                        python -m pytest tests/test_login.py -v --alluredir=reports/allure-results
                    '''
                }
            }
        }

        stage('Run UI Notes Tests') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    bat '''
                        call .venv\\Scripts\\activate

                        echo ==============================
                        echo RUNNING UI NOTES TESTS
                        echo HEADLESS=%HEADLESS%
                        echo ==============================

                        python -m pytest tests/test_product.py -v --alluredir=reports/allure-results
                    '''
                }
            }
        }

        stage('Run E2E Tests') {
            steps {
                catchError(
                    buildResult: 'UNSTABLE',
                    stageResult: 'FAILURE'
                ) {
                    bat '''
                        call .venv\\Scripts\\activate

                        echo ==============================
                        echo RUNNING E2E TESTS
                        echo HEADLESS=%HEADLESS%
                        echo ==============================

                        python -m pytest tests/test_e2e_hybrid.py -v --alluredir=reports/allure-results
                    '''
                }
            }
        }

        stage('Generate Final Allure Report') {
            steps {
                echo 'All test sections completed'
                echo 'Generating one combined Allure report'

                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[
                        path: 'reports/allure-results'
                    ]]
                ])
            }
        }

        stage('Archive Final Reports') {
            steps {
                archiveArtifacts(
                    artifacts: 'reports/**/*',
                    fingerprint: true,
                    allowEmptyArchive: true
                )

                echo 'Final reports archived successfully'
            }
        }
    }

    post {

        always {
            echo '================================'
            echo 'Pipeline execution completed'
            echo '================================'
        }

        success {
            echo 'All test stages completed successfully'
        }

        unstable {
            echo 'All test stages completed'
            echo 'One or more tests failed'
            echo 'Check the final combined Allure report'
        }

        failure {
            echo 'Pipeline infrastructure failed'
        }
    }
}
