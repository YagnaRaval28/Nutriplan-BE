from langgraph.graph import StateGraph, END
from app.ai.state import RecipeAgentState, MealPlanAgentState
from app.ai.nodes import (
    profile_analyzer, recipe_generator, nutrition_calculator,
    nutrition_validator, finalize_recipe, should_retry,
    meal_plan_profile_analyzer, meal_plan_generator,
)


def build_recipe_graph():
    graph = StateGraph(RecipeAgentState)

    graph.add_node("profile_analyzer", profile_analyzer)
    graph.add_node("recipe_generator", recipe_generator)
    graph.add_node("nutrition_calculator", nutrition_calculator)
    graph.add_node("nutrition_validator", nutrition_validator)
    graph.add_node("finalize_recipe", finalize_recipe)

    graph.set_entry_point("profile_analyzer")
    graph.add_edge("profile_analyzer", "recipe_generator")
    graph.add_edge("recipe_generator", "nutrition_calculator")
    graph.add_edge("nutrition_calculator", "nutrition_validator")

    graph.add_conditional_edges(
        "nutrition_validator",
        should_retry,
        {
            "retry": "recipe_generator",
            "finalize": "finalize_recipe",
            "end_with_error": END,
        },
    )
    graph.add_edge("finalize_recipe", END)

    return graph.compile()


def build_meal_plan_graph():
    graph = StateGraph(MealPlanAgentState)

    graph.add_node("profile_analyzer", meal_plan_profile_analyzer)
    graph.add_node("meal_plan_generator", meal_plan_generator)

    graph.set_entry_point("profile_analyzer")
    graph.add_edge("profile_analyzer", "meal_plan_generator")
    graph.add_edge("meal_plan_generator", END)

    return graph.compile()


recipe_graph = build_recipe_graph()
meal_plan_graph = build_meal_plan_graph()
