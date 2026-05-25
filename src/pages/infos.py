import streamlit as st
from utils.helpers import get_image, tte


def app(page: str, lang: str):
    upload_url = get_image("upload_csv.png")
    cleaned_data = get_image("clean_reviews.png")
    results_analysis = get_image("results.png")
    analyses = get_image("polarity_analysis.png")
    LINKED_IN = st.secrets["LINKED_IN"]
    st.markdown(
        f"""
        ## {tte(page=page,lang=lang,word="French Sentiments Analysis of the reviews")}
        {tte(page=page,lang=lang,word="This application allow you to make the analyse for the reviews dataset. To achieve your analyse, you need to follow the current steps :")}
        
        1.**{tte(page=page,lang=lang,word="Upload dataset")}** : 
        <img src="data:image/jpeg;base64,{upload_url}" alt="upload file" class="img-fluid">
        {tte(page=page,lang=lang,word="In this step, you must import the dataset of reviews.<br>**Remember that** : the name of your reviews column must be name's **text** in **lowercase**, otherwise you will receive an error during process of analyses.")}
        
        2.**{tte(page=page,lang=lang,word="Clean dataset")}** : 
        <img src="data:image/jpeg;base64,{cleaned_data}" alt="cleaned data" class="img-fluid">
        {tte(page=page,lang=lang,word="<br>In this step, you will clean the dataset of reviews to optimize the analyses of reviews.<br>**Note** : You can set the numbers of workers depend of your preference.<br>The times of this step depends of the size of your dataset and the number of workers fixed for the cleaning")}
        
        3.**{tte(page=page,lang=lang,word="Dataset analyses")}** : 
        <img src="data:image/jpeg;base64,{analyses}" alt="results analysis" class="img-fluid">
        {tte(page=page,lang=lang,word="<br>In this step,application will make the analyses of all cleaned dataset and produce results that you can interprete and make decisions. You can also set the number of workers for analyse<br>**Note** : The times of this step depends of the size of your dataset and the number of workers fixed for the analyse")}
        
        4.**{tte(page=page,lang=lang,word="Results of Analyses")}** : 
        <img src="data:image/jpeg;base64,{results_analysis}" alt="results analysis" class="img-fluid">
        {tte(page=page,lang=lang,word="<br>In this steps, application will be show some results for analyses.<br>**Note** : To show more results, you can go to the **Results** section")}
       
        5.{tte(page=page,lang=lang,word= "**Tip** : Application will give you instructions to achieve the goal of analyses.<br>You can use the left sidebar to discover application sections. You can also download all result of analyse if need.")}

        6.{tte(page=page,lang=lang,word="**RGPD** : You can delete your data at any time in the <b>Delete</b> section of the sidebar if you need.<br>If you have any suggestions, please share it with me on")} <a class="me-2" href="{LINKED_IN}">LinkedIn</a> {tte(page=page,lang=lang,word="to improve user experience, and application")}.<br>{tte(page=page,lang=lang,word="Thank you")}.
    """,
        unsafe_allow_html=True,
    )
