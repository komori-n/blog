import frontmatter


class Post:
    content: str
    title: str
    keywords: list[str]

    def __init__(self, filepath: str):
        with open(filepath, "r") as f:
            post = frontmatter.load(f)

        keywords = []
        for key in ["tags", "keywords", "categories"]:
            if key in post:
                keywords += post[key]

        self.content = post.content
        self.title = post["title"]
        self.keywords = keywords
