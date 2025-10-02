#!/usr/bin/env python
"""Example of creating a character learning progression with UNIHAN-ETL."""

from __future__ import annotations

from typing import Any

from unihan_etl.core import Packager


def test_learning_progression(unihan_quick_packager: Packager) -> None:
    """Demonstrate creating a progressive learning sequence."""
    # Note: kFrequency field is not in standard UNIHAN dataset
    # Create a packager with the fields we need
    modified_options = {
        "fields": ["kTotalStrokes", "kGradeLevel", "kMandarin"],
    }

    learning_packager = Packager(modified_options)

    # Download the data
    learning_packager.download()

    # Set format to python to get data back
    learning_packager.options.format = "python"

    # Get the data
    data = learning_packager.export()

    # Verify we have data
    assert data is not None
    assert len(data) > 0

    # Define a function to score character difficulty
    def calculate_difficulty(char_data: dict[str, Any]) -> float:
        """Calculate a difficulty score for a character based on various factors."""
        # Start with a base score
        difficulty = 5.0

        # Adjust for stroke count
        strokes = char_data.get("kTotalStrokes")
        if strokes:
            try:
                stroke_count = int(strokes[0] if isinstance(strokes, list) else strokes)
                # More strokes generally means more difficult
                difficulty += 0.5 * stroke_count
            except (ValueError, TypeError, IndexError):
                pass

        # Adjust for grade level
        grade = char_data.get("kGradeLevel")
        if grade:
            try:
                grade_level = int(grade[0] if isinstance(grade, list) else grade)
                # Lower grade level generally means easier character
                # E.g., grade 1 is easier than grade 6
                difficulty -= (6 - grade_level) * 1.5
            except (ValueError, TypeError, IndexError):
                pass

        # Ensure scores are within a reasonable range
        return max(1.0, min(10.0, difficulty))

    # Calculate difficulties for each character
    char_data_list = []
    if data is not None:
        for item in data:
            item_dict = dict(item)  # Convert mapping to dictionary
            item_dict["difficulty"] = calculate_difficulty(item_dict)
            char_data_list.append(item_dict)

    # Group characters into lessons based on difficulty
    def create_lessons(
        char_data: list[dict[str, Any]], num_lessons: int = 10
    ) -> list[list[dict[str, Any]]]:
        """Group characters into lessons based on difficulty."""
        # Sort characters by calculated difficulty
        sorted_chars = sorted(char_data, key=lambda x: x["difficulty"])

        # Create lesson groups
        lessons: list[list[dict[str, Any]]] = []
        if not sorted_chars:
            return lessons

        chars_per_lesson = max(1, len(sorted_chars) // num_lessons)

        for i in range(0, len(sorted_chars), chars_per_lesson):
            lesson = sorted_chars[i : i + chars_per_lesson]
            lessons.append(lesson)

        return lessons

    # Create lessons
    lessons = create_lessons(char_data_list)

    # Print some diagnostic info
    print(f"Found {len(data)} total characters")
    print(f"Created {len(lessons)} lessons")

    # Test the lesson structure if we have data
    if lessons:
        # Check a few lessons
        for i in range(min(3, len(lessons))):
            lesson = lessons[i]
            difficulty_range = [char["difficulty"] for char in lesson]
            avg_difficulty = (
                sum(difficulty_range) / len(difficulty_range) if difficulty_range else 0
            )
            print(
                f"Lesson {i + 1}: {len(lesson)} characters, "
                f"Avg difficulty: {avg_difficulty:.2f}"
            )

        # Verify lessons are in increasing difficulty
        if len(lessons) >= 2:
            first_lesson_avg = sum(char["difficulty"] for char in lessons[0]) / len(
                lessons[0]
            )
            last_lesson_avg = sum(char["difficulty"] for char in lessons[-1]) / len(
                lessons[-1]
            )
            assert first_lesson_avg <= last_lesson_avg
    else:
        # Just check the data structure if no lessons could be created
        for item in data[:5]:
            assert "char" in item
