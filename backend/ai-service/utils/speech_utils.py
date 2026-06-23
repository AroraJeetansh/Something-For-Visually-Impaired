def build_navigation_speech(results):

    if not results:
        return "No obstacles detected."

    messages = []

    for item in results[:3]:
         obj = item["object"].capitalize()

         if item["direction"] == "center":
            messages.append(
                f"{obj} ahead"
            )

         else:
            messages.append(
                f"{obj} on your {item['direction']}"
            )

    return ". ".join(messages)