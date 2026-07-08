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

        stage('Clean Previous Results') {
            steps {
                bat '''
                    if exist reports\\allure-results (
                        rmdir /s /q reports\\allure-results
                    )

                    if exist .pytest_cache_api (
                        rmdir /s /q .pytest_cache_api
                    )

                    if exist .pytest_cache_login (
                        rmdir /s /q .pytest_cache_login
                    )

                    if exist .pytest_cache_notes (
                        rmdir /s /q .pytest_cache_notes
                    )

                    if exist .pytest_cache_e2e (
                        rmdir /s /q .pytest_cache_e2e
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
                script {
                    def apiStatus = bat(
                        returnStatus: true,
                        script: '''
                            call .venv\\Scripts\\activate

                            echo ==============================
                            echo RUNNING ALL API TESTS
                            echo ==============================

                            python -m pytest tests/test_api_notes.py -v ^
                                -o cache_dir=.pytest_cache_api ^
                                --alluredir=reports/allure-results
                        '''
                    )

                    if (apiStatus != 0) {

                        echo 'API failures detected'
                        echo 'Rerunning only failed API tests'

                        def apiRetryStatus = bat(
                            returnStatus: true,
                            script: '''
                                call .venv\\Scripts\\activate

                                echo ==============================
                                echo RETRY FAILED API TESTS ONLY
                                echo ==============================

                                python -m pytest tests/test_api_notes.py -v --lf ^
                                    -o cache_dir=.pytest_cache_api ^
                                    --alluredir=reports/allure-results
                            '''
                        )

                        if (apiRetryStatus != 0) {
                            unstable('API tests still failing after retry')
                        } else {
                            echo 'Failed API tests passed on retry'
                        }

                    } else {
                        echo 'All API tests passed'
                    }
                }
            }
        }

        stage('Run UI Login Tests') {
            steps {
                script {
                    def loginStatus = bat(
                        returnStatus: true,
                        script: '''
                            call .venv\\Scripts\\activate

                            echo ==============================
                            echo RUNNING ALL UI LOGIN TESTS
                            echo HEADLESS=%HEADLESS%
                            echo ==============================

                            python -m pytest tests/test_login.py -v ^
                                -o cache_dir=.pytest_cache_login ^
                                --alluredir=reports/allure-results
                        '''
                    )

                    if (loginStatus != 0) {

                        echo 'UI Login failures detected'
                        echo 'Rerunning only failed UI Login tests'

                        def loginRetryStatus = bat(
                            returnStatus: true,
                            script: '''
                                call .venv\\Scripts\\activate

                                echo ==============================
                                echo RETRY FAILED UI LOGIN TESTS ONLY
                                echo HEADLESS=%HEADLESS%
                                echo ==============================

                                python -m pytest tests/test_login.py -v --lf ^
                                    -o cache_dir=.pytest_cache_login ^
                                    --alluredir=reports/allure-results
                            '''
                        )

                        if (loginRetryStatus != 0) {
                            unstable('UI Login tests still failing after retry')
                        } else {
                            echo 'Failed UI Login tests passed on retry'
                        }

                    } else {
                        echo 'All UI Login tests passed'
                    }
                }
            }
        }

        stage('Run UI Notes Tests') {
            steps {
                script {
                    def notesStatus = bat(
                        returnStatus: true,
                        script: '''
                            call .venv\\Scripts\\activate

                            echo ==============================
                            echo RUNNING ALL UI NOTES TESTS
                            echo HEADLESS=%HEADLESS%
                            echo ==============================

                            python -m pytest tests/test_product.py -v ^
                                -o cache_dir=.pytest_cache_notes ^
                                --alluredir=reports/allure-results
                        '''
                    )

                    if (notesStatus != 0) {

                        echo 'UI Notes failures detected'
                        echo 'Rerunning only failed UI Notes tests'

                        def notesRetryStatus = bat(
                            returnStatus: true,
                            script: '''
                                call .venv\\Scripts\\activate

                                echo ==============================
                                echo RETRY FAILED UI NOTES TESTS ONLY
                                echo HEADLESS=%HEADLESS%
                                echo ==============================

                                python -m pytest tests/test_product.py -v --lf ^
                                    -o cache_dir=.pytest_cache_notes ^
                                    --alluredir=reports/allure-results
                            '''
                        )

                        if (notesRetryStatus != 0) {
                            unstable('UI Notes tests still failing after retry')
                        } else {
                            echo 'Failed UI Notes tests passed on retry'
                        }

                    } else {
                        echo 'All UI Notes tests passed'
                    }
                }
            }
        }

        stage('Run E2E Tests') {
            steps {
                script {
                    def e2eStatus = bat(
                        returnStatus: true,
                        script: '''
                            call .venv\\Scripts\\activate

                            echo ==============================
                            echo RUNNING ALL E2E TESTS
                            echo HEADLESS=%HEADLESS%
                            echo ==============================

                            python -m pytest tests/test_e2e_hybrid.py -v ^
                                -o cache_dir=.pytest_cache_e2e ^
                                --alluredir=reports/allure-results
                        '''
                    )

                    if (e2eStatus != 0) {

                        echo 'E2E failures detected'
                        echo 'Rerunning only failed E2E tests'

                        def e2eRetryStatus = bat(
                            returnStatus: true,
                            script: '''
                                call .venv\\Scripts\\activate

                                echo ==============================
                                echo RETRY FAILED E2E TESTS ONLY
                                echo HEADLESS=%HEADLESS%
                                echo ==============================

                                python -m pytest tests/test_e2e_hybrid.py -v --lf ^
                                    -o cache_dir=.pytest_cache_e2e ^
                                    --alluredir=reports/allure-results
                            '''
                        )

                        if (e2eRetryStatus != 0) {
                            unstable('E2E tests still failing after retry')
                        } else {
                            echo 'Failed E2E tests passed on retry'
                        }

                    } else {
                        echo 'All E2E tests passed'
                    }
                }
            }
        }

        stage('Generate Final Allure Report') {
            steps {
                echo 'All four test sections completed'
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
            echo 'All test sections completed successfully'
        }

        unstable {
            echo 'Pipeline completed'
            echo 'One or more tests still failed after retry'
            echo 'Check the final combined Allure report'
        }

        failure {
            echo 'Pipeline infrastructure failed'
        }
    }
}
