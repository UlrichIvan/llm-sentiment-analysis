## French Sentiments Analysis of the reviews dataset.

This application allow you to make the sentiments analysis for your dataset using trained models :

- Regression Linear( LR )
- SVC( support vectors classifier )
- Camembert(using Transformer architecture and provider by Hugging Face plateform ).<br><br/>

To use the proposals service of application, you need to follow the current steps:

## Installation

- Requirements :
  1. OS : windows,MacOS, Linux
  2. Python>=3.12.10
  3. pip availble on command line(cmd,powershell,bash,ect.)
  4. IDE : VSCODE or other IDE like Pycharm
  5. Python avaible in your command line like pip

First clone this projet on your local machine :

```bash
git clone https://github.com/UlrichIvan/llm-sentiment-analysis.git
```

After it, move into the root of projet (llm-sentiment-analysis Folder) with command line or open the projet into our IDE ont the root of projet(`llm-sentiment-analysis` folder). use the command below to do that :

```bash
cd llm-sentiment-analysis
```

When the projet is open into your IDE(i recommand you to open projet into your IDE), you must create the isolation of your projet with virtual environment.<br/>
To mdo that, you can use the command below on the root of your projet(`llm-sentiment-analysis` folder) :

```bash
python -m venv .venv
```

This command wil be create the virtual environment(.venv Folder on the root of projet) for your project to isolate it and avoid the collision of others projet,that's the best pratice to use python on any projet.

When the virtual .venv is create , we must activate it to say `"hey python all dependencies must be install into the .venv environment"`.
To do that, we can use one command below depend on the OS of your machine.

```bash
# linux and macos use this command under the comment
source .venv/bin/activate

# windows with powershell, use the command below the comment
.\.venv\Scripts\Activate.ps1

# windows with cmd, use the command below the comment
.venv\Scripts\activate.bat
```

if you encounter and error with powershell, open the powershell terminal as Administrator and execute the command below

```pwsh
(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& .venv\Scripts\Activate.ps1)
```

After it you will see the virtual env activate on your terminal.
some terminal cannot show the virtual env. if you use vscode IDE you can see on the status bar below the .venv selected as environment when you open an python file, for example open the `main.py` file on the root of projet, you will the `.venv` environment selected.

Make sure that the virtual env .venv has been actived successfully to go on the next steps, otherwise you can encounter the error if some projet on your computer use the same packages with this projet.

After .venv activate, you can install all dependencies into requirement.txt in the root of projet(`llm-sentiment-analysis` folder) with the command below :

First install torch for cpu (this is required before the installation of requirements.txt dependencies)

```bash
pip install torch==2.12.0+cpu --extra-index-url https://download.pytorch.org/whl/cpu
```

This command will be install torch for cpu on your virtual env. now when you will install transformers for hugging face, it will detect that you have installed torch for cpu, then it will install the appropriate transformers for cpu.
If this step is not execute in this order, maybe you will encounter and error if GPU not support by your computer.<br>

After it, you will run the command below to install the rest of dependencies;

```bash
pip install -r requirements.txt
```

This command will be install all dependencies into,the virtual env of projet.

In the next step, we are going to download one file verify necessary for our projet. Indeed after the train of Camembert LLM, the hugging Face librarie(Transformers) had generated many files that one very important is the `model.safetensors`, but this file is very large and i encounter and error with github to push that on this repository, that's the reason we must download the file on google drive. To do that just clik on the link below : <br>
[Download model.safetensors file here](https://drive.google.com/file/d/1ecC2IObgN6Y9Tv5zuT-DfRKB0CLdsmHb/view?usp=drive_link)

After the download fihish, you will move the file into the Camembert folder into the `src/models/Camembert` folder.
in this `src/models` folder, you will see others models trained with `scikit-learn` librairie for the same task`(sentiments analysis)`.

Camembert model is the new trained model with `Hugging Face` librairie to achieve the same task`(sentiments analysis)`.

After all the previous steps, you can run the projet and use it, just run the command below :

```bash
streamlit run .\main.py
```

this command will be run the projet on your localhost, just follow the link to show the result and enjoy with it.

## About Application

This projet use the [Streamlit](https://streamlit.io/) librairie to make all results that you will see as UI Experience. I have also make some custom css to provide the good appear of application like the sidebar and other part of application that you will see.

The dataset must be contains the `text` columns that content the reviews of users, that is and [exemple of dataset](https://drive.google.com/file/d/1GBoRp3hQg62e13osfRRTJBZ2ZP46b6wW/view?usp=drive_link) that you can use with application.

Clik [here to download dataset](https://drive.google.com/file/d/1GBoRp3hQg62e13osfRRTJBZ2ZP46b6wW/view?usp=drive_link)
that you will import in the `Analyses` page.

If the format of dataset is not respet, you will get and error message from application to indicate you this explanation.

This application has five pages :

- `Home`: This page present the goal and quick preview of the application, and the `Get's started` button to start using the application.
- `Analyses` : this page allow you to make all analyse for your dataset and see the miminal result after it.
- `Results` : this page allow you to see all results associate to all model use in the `Analyses` page to make analyse of
  dataset.
- `Infos` : This page describes the differents steps to achive the best analyse of your Dataset.
- `About` : This page give the informations about the Authors of this projet.
- `Logout` : this page logout user to the application.

You can also change the language uses in application like you want.<br>
Application support four Language :

- en : for english language
- fr : for French language
- es : for spain language
- de : for Deustch language

`Remarks` : you can encounter not results or disable button analyse when you select and run analyse for the first time with Camembert model, this is because the load of model for the first time take some time, after it the model wil be cacched by streamlit and the rest of time model should be quickly to load, it's the advantages of cache use into Streamlit.

## About Analyse

in the application, we have two type of models :

- `Sklearn models` : the models trained using scikit-learn
- `Hugging Face model` : the model trained using hugging face Transformers librairie.

the disference for the two type of model is that :

- `sklearn models` must be receive the cleaned text to perform with the analyses of text, ortherwise the model will be make the overfitting or under fitting during the train of models.
- `Hugging Face model` not necessary need the cleaning text to perform on the of text, because it uses the Transformer architecture, why ? because the goal of the application is to make the `text-classification`,then only the `encoder` can achive this task, this is because we are selected camembert LLM.

That is the raison you will see the `cleaning step` before the `analyse step` in the `analyse page`, but internaly `Camembert` model not use it to analyse our dataset.

Other reason that we are choose camembert LLM is that it's training on the french language, because our projet can only make the analyse of french reviews.

In the results pages, into the more results, you will see some words like emojies, url, etc. on the negative and positive words,But you will never see it for others models, that is because sklearn model use the cleaning dataset and hugging Face not use the cleaned dataset in the case of our application.

## Refresh Analyse

In the application, on the sidebar, when you run analyse of application, you can see the `Refresh` button that allow you to reset or refresh the `Analyse` page if you need it or if some button cannot be clicked.
I added it, to provide the control of user to reset the `Analyse` page when he or she needs or to cancel some disable utils buttons found on the `Analyse` page.

## Training Camembert model

To see how i will trained Camembert model on CPU, you can see the `llm_sentiments_analysis.ipynb` notebook on the root of projet that describe all steps and analyses necessary to achieve the goal of our projet for Camembert model.

## Summary

Thank you for your attention, for this projet.
If you have any need about IA projets, CDI, CDD contact [me](https://www.linkedin.com/in/ulrich-chokomeny/) by message on linkedin or recommand me to any enterprise that i will provide my knowledge.<br/>
Best regard.
