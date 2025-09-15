
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.chains import create_retrieval_chain

def _build_chain(llm, top_k: int = 4, vector_store = None):
    if vector_store is not None:
        retriever = vector_store.as_retriever(search_kwargs={"k": top_k})

        system_template = (
            "You are an assistant that answers user questions using the provided context. "
            "If the answer is not contained in the context, say \"I don't know.\" "
            "Be concise and return the answer, then list sources (source_id and chunk_index)."
        )
        system_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_template = "{input}"  
        human_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

        chain = create_retrieval_chain(retriever=retriever, llm=llm, prompt=chat_prompt, return_source_documents=True)
        return chain