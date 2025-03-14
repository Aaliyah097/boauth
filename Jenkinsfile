pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    app: kaniko
spec:
  containers:
    - name: kaniko
      image: gcr.io/kaniko-project/executor:debug
      command:
        - tail
        - "-f"
        - /dev/null
      tty: true
      volumeMounts:
        - name: regcred
          mountPath: /kaniko/.docker/config.json
          subPath: .dockerconfigjson
    - name: kubectl
      image: lachlanevenson/k8s-kubectl:v1.21.0
      command:
        - tail
        - "-f"
        - /dev/null
      tty: true
  volumes:
    - name: regcred
      secret:
        secretName: regcred
"""
        }
    }

    environment {
      IMAGE_NAME = 'aaliyah097/boauth'
    }

    stages {
        stage('Checkout') {
          steps {
            // В Multibranch Pipeline Jenkins сам клонирует репозиторий,
            // но если нужно, можно явно указать checkout:
            checkout scm
          }
        }
        stage('Set Image Tag') {
          steps {
            script {
              // Получаем короткий хэш коммита (7 символов)
              env.IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
              echo "Using commit hash as image tag: ${env.IMAGE_TAG}"
            }
          }
        }
        stage('Build Docker Image with Kaniko') {
          steps {
            container('kaniko') {
              sh '''
              /kaniko/executor \
                --context=`pwd` \
                --dockerfile=Dockerfile \
                --destination=${IMAGE_NAME}:${IMAGE_TAG} \
                --verbosity=debug
              '''
            }
          }
        }
        stage('Update Deployment Manifest') {
          steps {
            // Обновляем манифест, подставляя новый тег
            sh """
                sed -i 's|image: .*|image: ${IMAGE_NAME}:${IMAGE_TAG}|' ci-cd/deployment.yaml
            """
          }
        }
        stage('Deploy to Kubernetes') {
          steps {
            script{
              def targetNamespace = ''
              if (env.BRANCH_NAME == 'develop') {
                  targetNamespace = 'dev'
              } else if (env.BRANCH_NAME == 'main') {
                  targetNamespace = 'prod'
              } else {
                  error "Unsupported branch: ${env.BRANCH_NAME}"
              }
              echo "Deploying to namespace: ${targetNamespace}"

              container('kubectl') {
                sh "kubectl apply -f ci-cd/deployment.yaml -n ${targetNamespace}"
                sh "kubectl apply -f ci-cd/service.yaml -n ${targetNamespace}"
              }
            }
          }
        }
    }
}
