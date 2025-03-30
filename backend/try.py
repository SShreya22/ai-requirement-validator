from openai import OpenAI

client = OpenAI(api_key="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")
models = client.models.list()
print(models)
