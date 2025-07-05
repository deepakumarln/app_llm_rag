import os
import asyncio
from openai import AsyncOpenAI

KEY = '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'


text = '''(SCHWETER und AKBIK, 2020) proposes document-level features from transformer
based architectures, these can be obtained by passing a sentence with its surrounding
context to obtain word embeddings for the words in the sentences. For each sentence
to be classiﬁed, 64 tokens of the left and right context (sentence) are added.
Figure 2.8: Extraction of Document Level Features (SCHWETER und AKBIK, 2020)
From the above ﬁgure, we can see for the sentence "I love Paris" (shown in green), 64
tokens of the previous and next sentence are added (show in blue). When the self-
attention is calculated for each word in the sentence, the representations of the sentence
are inﬂuenced by these left and right context.
Since each sentence and its context need to be passed through the transformer only
once, and that the added context is limited to small window, this approach has compu-
tational and implementation advantages.
4.3 FLERT Model
We observed that we were in need of a model to capture the contexts of words in the sen-
tences of the document better. We tried the (SCHWETER und AKBIK, 2020) model, which
captures document level contextual features by using the previous and next sentences
for a particular sentence to get document level features. The model uses XLM-RoBERTa-
Large transformer with a linear layer ﬁne tuned for the task of NER. This model was able
to give us a F1 score of 87% on the manually annotated documents. This is because the
documents had many pages with big sentences, and since this model uses document
level features the model is able to send better embeddings for the sentences to the trans-
former, with these better embeddings for the words in the sentences the XLM-RoBERTa
transformer correctly identiﬁes the classes of the individual words in the sentences.
Figure 4.2: F1 Scores of Models on OntoNotes 5.0 and Annotated Documents'''
question = 'explain about the document level features'
USER_PROMPT = f"""
    Use the following pieces of information enclosed in <context> tags to provide an answer to the question enclosed in <question> tags.

    <context>
    {text}
    </context>

    <question>
    {question}
    </question>"""

client = AsyncOpenAI(
    # This is the default and can be omitted
    api_key=KEY,
)

#completion = client.chat.completions.create(
#    model="gpt-4o",
#    messages=[
#        {"role": "developer", "content": "Talk like a pirate."},
#        {
#            "role": "user",
#            "content": "How do I check if a Python object is an instance of a class?",
#        },
#    ],
#)

async def main() -> None:
    completion = await client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "assistant", "content": "provide answers to user questions"},
        {
            "role": "user",
            "content": USER_PROMPT,
        },
    ],
)
    print(completion.choices[0].message.content)


asyncio.run(main())