import streamlit as st
from streamlit_option_menu import option_menu
from src.pages import about, delete, home as analyse, infos, logout, results
from src.pages.login import app as Login
from utils.tools import (
    LANGUAGES,
    MENUS,
    OPTION_MENU_STYLE,
)


class App:
    def __init__(self):
        if "language" not in st.session_state:
            st.session_state["language"] = "en"
        if "page_index" not in st.session_state:
            st.session_state["page_index"] = -1
        if "menu_selected" not in st.session_state:
            st.session_state["menu_selected"] = None
        if "is_loading" not in st.session_state:
            st.session_state["is_loading"] = False


        self.options_menus = []
        self.pages = []
        self.options_icons = []
        self.options_menus = []
        

        if st.user.get("is_logged_in") and st.user.get("email_verified"):
            actions = [
                analyse.app,
                results.app,
                infos.app,
                about.app,
                logout.app,
            ]
            self.options_menus = list(MENUS[st.session_state["language"]].keys())
            self.options_icons = list(MENUS[st.session_state["language"]].values())
            for i, menu in enumerate(self.options_menus):
                self.pages.append({"menu": menu, "fn": actions[i]})

            st.session_state["page_index"] = (
                2
                if st.session_state["page_index"] == -1
                else st.session_state["page_index"]
            )
            st.session_state["menu_selected"] = self.options_menus[
                st.session_state["page_index"]
            ]


    def get_menu_by_lang(self, lang) -> tuple | None:
        if lang in list(MENUS.keys()):
            menus = MENUS[lang]
            OPTION_MENU_ICONS = list(menus.values())
            OPTION_MENU_ITEMS = list(menus.keys())
            return OPTION_MENU_ITEMS, OPTION_MENU_ICONS

    def sidebar_style(self):
        st.sidebar.markdown(
            f"""
                  <style>
                    [data-testid="stVerticalBlock"]{{
                        gap:0px;
                    }}
                    [data-testid="stSidebarContent"]{{
                        background-color:#123;
                    }}
                    [data-testid="stSidebarUserContent"]{{
                        padding: 0px;
                    }}
                    [data-testid="stSidebarCollapseButton"]{{
                        display:block;
                        order : 3;
                        margin-left: auto;
                    }}
                    [data-testid="stBaseButton-headerNoPadding"]:hover{{
                        color:white!important;
                    }}
                    [data-testid="stElementContainer"]{{
                        margin: auto;
                    }}
                    [data-testid="data-testid="stMarkdown"] [data-testid="stMarkdownContainer"]{{
                        display: flex;
                        justify-content: center;
                        align-items: center;
                    }}
                    [data-testid="stSidebarHeader"]:hover [data-testid="stSidebarCollapseButton"]{{
                        color:white!important;
                    }}
                    [data-testid="stSidebarHeader"]{{
                        display : {"flex" if st.user.get("is_logged_in") else "none!important"};
                        align-items:center;
                        padding-bottom:0px;
                    }}
                    [data-testid="stLogo"]{{
                        width: 50px;
                        height: 50px;
                        border-radius: 50%;
                        order:1
                    }}
                    div.stElementContainer.element-container.st-key-lang{{
                        padding: 1rem;
                        position: fixed;
                        bottom: 0;
                    }}
                  </style>  
                """,
            unsafe_allow_html=True,
        )

    def set_page_index(self, key: str) -> None:
        st.session_state["page_index"] = self.options_menus.index(st.session_state[key])

    def set_lang(self, page_index: int) -> None:
        if st.session_state["language"] != st.session_state["lang"]:
            st.session_state["language"] = st.session_state["lang"]
            if st.session_state["language"] != LANGUAGES[0]:
                values = list(MENUS[st.session_state["language"]].values())
                st.session_state["menu_selected"] = values[page_index]
            else:
                values = list(MENUS[LANGUAGES[0]].values())
                st.session_state["menu_selected"] = values[page_index]

    def run(self):
        if st.user.get("is_logged_in") and st.user.get("email_verified"):
            # load css
            self.sidebar_style()
            # display side bar
            self.sidebar()
            # display view
            self.view()
        else:
            Login()

    def view(self):
        for _, page in enumerate(self.pages):
            if st.session_state["menu_selected"] == page.get("menu"):
                fn = page.get("fn")
                if fn is not None:
                    fn(
                        page=st.session_state["menu_selected"],
                        lang=st.session_state["language"],
                    )
                    break

    def sidebar(self):
        with st.sidebar:
            option_menu(
                menu_title=None,
                options=self.options_menus,
                icons=self.options_icons,
                menu_icon="emoji-kiss-fill",
                default_index=st.session_state["page_index"],
                styles=OPTION_MENU_STYLE,
                key="menu",
                on_change=self.set_page_index,
            )
            st.selectbox(
                label=" ",
                options=LANGUAGES,
                key="lang",
                index=LANGUAGES.index(st.session_state["language"]),
                on_change=self.set_lang,
                args=(int(st.session_state["page_index"]),),
                disabled=st.session_state["is_loading"]
            )


try:
    App().run()
except Exception as e:
   raise e
