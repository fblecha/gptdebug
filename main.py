import argparse
import json

from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ConversationNode:
    def __init__(self, user_input="", llm_response="", depth=0, is_current=False):
        self.user_input = user_input
        self.llm_response = llm_response
        self.children = []
        self.depth = depth
        self.is_current = is_current  # Indicates the current (most recent) node

    def add_child(self, user_input, llm_response, is_current=False):
        child = ConversationNode(user_input, llm_response, self.depth + 1, is_current)
        self.children.append(child)
        return child


class ConversationTree:
    def __init__(self):
        self.root = ConversationNode()
        self.current_node = self.root

    def add_to_conversation(self, user_input, llm_response):
        # Mark the current node as not current before adding a new one
        if self.current_node:
            self.current_node.is_current = False
        new_node = self.current_node.add_child(user_input, llm_response, is_current=True)
        self.current_node = new_node
        # ... rest of the class

    def to_dict(self, node=None):
        if node is None:
            node = self.root

        node_dict = {
            "user_input": node.user_input,
            "llm_response": node.llm_response,
            "children": [self.to_dict(child) for child in node.children]
        }

        return node_dict


    def save_conversation(self, filename="conversation.json"):
        conversation_dict = self.to_dict()
        with open(filename, 'w') as file:
            json.dump(conversation_dict, file, indent=4)
        print(f"Conversation saved to {filename}")


    def delete_current_node(self):
        if self.current_node == self.root:
            print("Cannot remove the root node.")
            return

        # Find the parent of the current node
        parent = self.find_parent(self.root, self.current_node)
        if parent:
            # Remove the current node from its parent's children
            parent.children = [child for child in parent.children if child != self.current_node]
            # Set the parent as the new current node
            self.current_node = parent
            self.current_node.is_current = True
        else:
            print("Error: Parent node not found.")


    def move_up(self):
        if self.current_node and self.current_node is not self.root:
            # Set the current node's is_current to False
            self.current_node.is_current = False

            # Find the parent of the current node
            parent = self.find_parent(self.root, self.current_node)
            if parent:
                # Set the parent as the new current node
                self.current_node = parent
                self.current_node.is_current = True

    def find_parent(self, node, child):
        if child in node.children:
            return node
        for next_node in node.children:
            parent = self.find_parent(next_node, child)
            if parent:
                return parent
        return None

    def display_line_to_current(self, node=None, path=None):
        if node is None:
            node = self.root
            path = []

        # Add this node to the path
        path.append(node)

        if node.is_current:
            # Print the path when the current node is reached
            for step in path:
                if step.user_input or step.llm_response:
                    current_marker = "*" if step.is_current else " "
                    print(f"{current_marker}User: {step.user_input}")
                    print(f"  LLM: {step.llm_response}")
            return

        for child in node.children:
            self.display_line_to_current(child, path.copy())


    def list_children(self):
        if not self.current_node.children:
            print("No more branches to follow.")
            return
        print("Select a branch to follow:")
        for i, child in enumerate(self.current_node.children):
            print(f"{i + 1}: {child.user_input}")

    def display_conversation(self, node=None, indent=0):
        if node is None:
            node = self.root

        prefix = "*" if node.is_current else " "
        if node.user_input or node.llm_response:
            print("  " * indent + f"{prefix} User: {node.user_input}")
            print("  " * indent + f"  LLM: {node.llm_response}")

        for child in node.children:
            self.display_conversation(child, indent + 1)

    def display_tree(self, node=None, prefix=""):
        if node is None:
            node = self.root

        # Determine the symbols for tree branches
        connector = "├── " if node is not self.root else ""
        current_marker = "*" if node.is_current else " "

        if node.user_input or node.llm_response:
            print(f"{prefix}{connector}{current_marker}User: {node.user_input}")
            print(f"{prefix}{connector}  LLM: {node.llm_response}")

        for i, child in enumerate(node.children):
            is_last = i == len(node.children) - 1
            # Adjust the prefix for child nodes
            child_prefix = prefix + ("│   " if not is_last else "    ")
            self.display_tree(child, child_prefix)




    def go_back(self):
        # Implement logic to step back in the conversation tree
        print("go back")


    def branch_conversation(self, user_input, llm_response):
        # Implement logic to branch the conversation from the current node
        print("branch conversation")



def handle_exit():
    print("Exiting REPL...")
    exit()

def handle_help():
    print("Available commands: :exit, :help, ...")

def handle_context():
    print("write the conversation context here")



def llm_function_echo(user_input):
    # In a real application, this function would interact with a language model
    # and return its response. Here, it's just a placeholder.
    llm_response = f"LLM Echo: {user_input}"
    return llm_response



def llm_function(user_input):
    try:
        completion = client.chat.completions.create(
        # model="gpt-3.5-turbo",  
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
            ]
        )

        print(completion.choices[0].message)
    except Exception as e:
        return f"An error occurred: {e}"



def repl():
    conversation_tree = ConversationTree()


    while True:
        try:
            # REPL logic
            user_input = input("REPL> ")
            # llm_response = llm_function(user_input)  # Get the response from the LLM
            # conversation_tree.add_to_conversation(user_input, llm_response)
            # More REPL logic



            if user_input.startswith(":"):
                # Handle special commands
                if user_input in [":exit", ":q"]:
                    handle_exit()
                elif user_input in [":help", ":h"]:
                    handle_help()
                elif user_input in [":context", ":c"]:
                    conversation_tree.display_conversation()
                    # handle_context()
            
                elif user_input == ":rm":
                    conversation_tree.delete_current_node()

                elif user_input == ":tree":
                    conversation_tree.display_tree()
                    continue

                elif user_input == ":line":
                    conversation_tree.display_line_to_current()

                elif user_input.startswith(":save"):
                    filename = user_input.split(maxsplit=1)[1] if len(user_input.split()) > 1 else "conversation.json"
                    conversation_tree.save_conversation(filename)

                elif user_input == ":up":
                    conversation_tree.move_up()

                elif user_input.startswith(":down"):
                        if conversation_tree.current_node.children:
                            conversation_tree.list_children()
                            choice = input("Enter the number of the branch to follow: ")
                            try:
                                choice = int(choice) - 1
                                if 0 <= choice < len(conversation_tree.current_node.children):
                                    conversation_tree.current_node.is_current = False
                                    conversation_tree.current_node = conversation_tree.current_node.children[choice]
                                    conversation_tree.current_node.is_current = True
                                else:
                                    print("Invalid choice.")
                            except ValueError:
                                print("Please enter a valid number.")
                        else:
                            print("No child nodes to move down to.")
                    
                else:
                    print(f"Unknown command: {user_input}")
            else:
                # Get the response from the LLM and add it to the conversation tree
                llm_response = llm_function(user_input)
                conversation_tree.add_to_conversation(user_input, llm_response)

                # Optionally, display the LLM's response immediately
                print(llm_response)

        except KeyboardInterrupt:
            print("\nInterrupted. Use :exit to exit the REPL.")
        except Exception as e:
            print(f"Error: {e}")




def main(args):
    # Example function body with arguments
    # print(f"Hello, {args.name}!")
    repl()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example script.")
    parser.add_argument('--name', type=str, default='World', help='Name to greet')
    args = parser.parse_args()
    main(args)
