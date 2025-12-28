In every sample you use in the documents you write you must assume the UV as the default package and environment manager.

When verifying a document, create a dedicated directory to store test scripts and all code related to the verification process. In case of Python code, use `uv` to manage the environment and dependencies for these tasks. In case of Node.js code, use Typescript instead of Javascript and 'npm' to manage the environment and dependencies for these tasks. The folder must be named inspired by the document to verify and it must be placed in the same directory as the document to verify.

