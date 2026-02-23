from langchain_core.prompts import ChatPromptTemplate
from src.state import JudicialOpinion, AgentState
from langchain_openai import ChatOpenAI

# Initialize LLM with Structured Output
llm = ChatOpenAI(model="gpt-4o").with_structured_output(JudicialOpinion)


def create_judge_node(persona: str, instruction: str):
    """Factory function to create judge nodes with distinct personas."""
    
    def judge_node(state: AgentState) -> AgentState:
        """
        Judicial Protocol: Distinct Personas.
        Must return structured JudicialOpinion.
        """
        # Gather Evidence
        all_evidence = []
        for group in state.get("evidences", {}).values():
            all_evidence.extend(group)
            
        evidence_text = "\n".join([f"- {e.location}: {e.content}" for e in all_evidence])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are the {persona}. {instruction}"),
            ("human", "Evidence:\n{evidence}\n\nRubric Criterion: {criterion}"),
        ])
        
        chain = prompt | llm
        result = chain.invoke({
            "evidence": evidence_text, 
            "criterion": "langgraph_architecture"
        })
        
        return {"opinions": [result]}
    
    return judge_node


# Instantiate Personas with Distinct Philosophies
prosecutor_node = create_judge_node(
    "Prosecutor", 
    "Trust No One. Assume Vibe Coding. Scrutinize for security flaws and laziness."
)

defense_node = create_judge_node(
    "Defense Attorney", 
    "Reward Effort and Intent. Look for the Spirit of the Law."
)

tech_lead_node = create_judge_node(
    "Tech Lead", 
    "Does it actually work? Is it maintainable? Be pragmatic."
)
