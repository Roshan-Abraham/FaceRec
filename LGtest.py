from typing import Annotated, List, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, MessagesState, START, StateGraph
import operator

# Base Models for Movie Components
class Character(BaseModel):
    name: str = Field(description="Character name")
    role: str = Field(description="Role in story (protagonist, antagonist, etc.)")
    background: str = Field(description="Character backstory and motivation")
    arc: str = Field(description="Character development arc")
    personality: str = Field(description="Key personality traits")

class Plot(BaseModel):
    premise: str = Field(description="Core story premise")
    synopsis: str = Field(description="Detailed plot synopsis")
    setting: str = Field(description="Story setting and world-building")
    turning_points: List[str] = Field(description="Major plot points")
    resolution: str = Field(description="Story resolution")

class Theme(BaseModel):
    main_theme: str = Field(description="Primary theme")
    moral: str = Field(description="Core message or moral")
    subthemes: List[str] = Field(description="Supporting themes")

class Screenplay(BaseModel):
    acts: List[str] = Field(description="Major screenplay acts")
    key_scenes: List[str] = Field(description="Critical scenes")
    dialogue: List[str] = Field(description="Key dialogue moments")

class MarketAnalysis(BaseModel):
    target_audience: List[str] = Field(description="Primary audience demographics")
    genre_positioning: str = Field(description="Genre and market positioning")
    unique_selling_points: List[str] = Field(description="Key marketing points")
    comparisons: List[str] = Field(description="Similar successful movies")

# State Classes
class MovieState(MessagesState):
    concept: str
    plot: Optional[Plot] = None
    characters: List[Character] = []
    theme: Optional[Theme] = None
    screenplay: Optional[Screenplay] = None
    market_analysis: Optional[MarketAnalysis] = None
    director_notes: List[str] = []
    critic_feedback: List[str] = []
    user_feedback: Annotated[list, operator.add] = []

# Initialize LLM
llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Node Functions
def develop_plot(state: MovieState):
    """Creates initial plot based on concept"""
    system_prompt = """You are a master plot developer. Create a compelling plot from the given concept.
    Consider genre conventions while being innovative. Focus on creating unexpected but satisfying story beats."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Develop a plot for this concept: {state['concept']}")
    ]
    
    # Use structured output
    plot_llm = llm.with_structured_output(Plot)
    plot = plot_llm.invoke(messages)
    
    return {"plot": plot}

def create_characters(state: MovieState):
    """Develops characters that serve the plot"""
    system_prompt = """You are a character development expert. Create compelling characters 
    that will drive the plot forward while experiencing meaningful growth."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Create characters for this plot: 
        {state['plot'].synopsis}
        Consider the theme and ensure character arcs support it.""")
    ]
    
    # Structure output for multiple characters
    character_llm = llm.with_structured_output(List[Character])
    characters = character_llm.invoke(messages)
    
    return {"characters": characters}

def develop_theme(state: MovieState):
    """Extracts and develops themes from plot and characters"""
    system_prompt = """You are a thematic analyst. Identify and develop meaningful themes 
    that emerge from the story and characters."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Analyze this plot and these characters for themes:
        Plot: {state['plot'].synopsis}
        Characters: {[c.dict() for c in state['characters']]}""")
    ]
    
    theme_llm = llm.with_structured_output(Theme)
    theme = theme_llm.invoke(messages)
    
    return {"theme": theme}

def write_screenplay(state: MovieState):
    """Converts plot into screenplay format"""
    system_prompt = """You are a screenplay writer. Transform the plot into a 
    structured screenplay while maintaining character voices and themes."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Write a screenplay based on:
        Plot: {state['plot'].dict()}
        Characters: {[c.dict() for c in state['characters']]}
        Theme: {state['theme'].dict()}""")
    ]
    
    screenplay_llm = llm.with_structured_output(Screenplay)
    screenplay = screenplay_llm.invoke(messages)
    
    return {"screenplay": screenplay}

def director_review(state: MovieState):
    """Reviews and provides directorial guidance"""
    system_prompt = """You are a film director. Review the screenplay and provide 
    notes on visualization, pacing, and dramatic impact."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Review this screenplay:
        {state['screenplay'].dict()}""")
    ]
    
    response = llm.invoke(messages)
    
    return {"director_notes": [response.content]}

def critic_review(state: MovieState):
    """Provides critical analysis and feedback"""
    system_prompt = """You are a film critic. Analyze the story for potential 
    strengths and weaknesses, considering artistic merit and audience appeal."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Review this film concept:
        Plot: {state['plot'].dict()}
        Theme: {state['theme'].dict()}
        Screenplay: {state['screenplay'].dict()}""")
    ]
    
    response = llm.invoke(messages)
    
    return {"critic_feedback": [response.content]}

def market_analysis(state: MovieState):
    """Analyzes market potential and target audience"""
    system_prompt = """You are a film marketing expert. Analyze the market potential 
    and identify target demographics."""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"""Analyze market potential for:
        Plot: {state['plot'].synopsis}
        Theme: {state['theme'].main_theme}
        Critic Feedback: {state['critic_feedback']}""")
    ]
    
    market_llm = llm.with_structured_output(MarketAnalysis)
    analysis = market_llm.invoke(messages)
    
    return {"market_analysis": analysis}

def handle_user_feedback(state: MovieState):
    """Process point where user can provide feedback"""
    # This is a no-op node that will be interrupted for user input
    pass

def route_feedback(state: MovieState):
    """Routes the workflow based on user feedback"""
    feedback = state.get('user_feedback', [])
    if not feedback:
        return END
    
    latest_feedback = feedback[-1].lower()
    
    # Route based on feedback keywords
    if 'plot' in latest_feedback:
        return 'develop_plot'
    elif 'character' in latest_feedback:
        return 'create_characters'
    elif 'theme' in latest_feedback:
        return 'develop_theme'
    elif 'screenplay' in latest_feedback:
        return 'write_screenplay'
    else:
        return END

# Build Graph
workflow = StateGraph(MovieState)

# Add nodes
workflow.add_node("develop_plot", develop_plot)
workflow.add_node("create_characters", create_characters)
workflow.add_node("develop_theme", develop_theme)
workflow.add_node("write_screenplay", write_screenplay)
workflow.add_node("director_review", director_review)
workflow.add_node("critic_review", critic_review)
workflow.add_node("market_analysis", market_analysis)
workflow.add_node("handle_user_feedback", handle_user_feedback)

# Add edges
workflow.add_edge(START, "develop_plot")
workflow.add_edge("develop_plot", "create_characters")
workflow.add_edge("create_characters", "develop_theme")
workflow.add_edge("develop_theme", "write_screenplay")
workflow.add_edge("write_screenplay", "director_review")
workflow.add_edge("director_review", "critic_review")
workflow.add_edge("critic_review", "market_analysis")
workflow.add_edge("market_analysis", "handle_user_feedback")
workflow.add_conditional_edges(
    "handle_user_feedback",
    route_feedback,
    {
        "develop_plot": "develop_plot",
        "create_characters": "create_characters",
        "develop_theme": "develop_theme",
        "write_screenplay": "write_screenplay",
        END: END
    }
)

# Compile graph with user feedback interruption
graph = workflow.compile(interrupt_before=['handle_user_feedback'])

# Example usage
initial_state = {"concept": "A time-traveling chef who must cook meals that change historical events"}
result = graph.invoke(initial_state)
