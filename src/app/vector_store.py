import chromadb
from typing import List, Dict
from app.config import config


class VectorStore:
    def __init__(self):
        print(
            f"Connecting to Chroma DB at {config.CHROMA_SERVER_HOST}:{config.CHROMA_SERVER_HTTP_PORT}"
        )
        self.client = chromadb.HttpClient(
            host=config.CHROMA_SERVER_HOST,
            port=config.CHROMA_SERVER_HTTP_PORT,
        )
        self.collection = self.client.get_or_create_collection("churning_discussions")
        print("Vector store initialized")

    def add_documents(self, posts: List[Dict]):
        """Add documents to the vector store"""
        total_comments = sum(len(post["comments"]) for post in posts)
        print(f"Adding {total_comments} comments to vector store...")

        for post in posts:
            print(f"Processing post from {post['date']}")
            # Create a map of comment IDs to their replies and scores
            comment_map = {comment["id"]: comment for comment in post["comments"]}

            for comment in post["comments"]:
                # Get the parent comment if it exists
                parent_content = ""
                parent_score = 0
                if comment["parent_id"].startswith(
                    "t1_"
                ):  # t1_ prefix indicates a comment
                    parent_id = comment["parent_id"][3:]  # Remove t1_ prefix
                    if parent_id in comment_map:
                        parent = comment_map[parent_id]
                        parent_content = f"Parent comment: {parent['body']}\nParent score: {parent['score']}"
                        parent_score = parent["score"]

                document = (
                    f"Date: {post['date']}\n"
                    f"Comment score: {comment['score']}\n"
                    f"{parent_content}\n"
                    f"Comment: {comment['body']}"
                )

                self.collection.add(
                    documents=[document],
                    ids=[comment["id"]],
                    metadatas=[
                        {
                            "post_date": post["date"],
                            "score": comment["score"],
                            "parent_id": comment["parent_id"],
                            "parent_score": parent_score,
                        }
                    ],
                )
        print("Documents added to vector store")

    def query(self, query_text: str, n_results: int = 5):
        """Query the vector store for relevant discussions"""
        print(f"Querying vector store: '{query_text[:50]}...'")
        results = self.collection.query(query_texts=[query_text], n_results=n_results)
        print(f"Found {len(results['documents'][0])} relevant documents")
        return results

    def delete_collection(self):
        """Delete all documents from the collection"""
        print("Deleting all documents from vector store...")
        try:
            # Get all document IDs
            all_docs = self.collection.get()
            if all_docs and all_docs["ids"]:
                # Delete all documents by their IDs
                self.collection.delete(ids=all_docs["ids"])
                print(f"Deleted {len(all_docs['ids'])} documents from vector store")
            else:
                print("No documents to delete")
        except Exception as e:
            print(f"Error during deletion: {str(e)}")
            raise
