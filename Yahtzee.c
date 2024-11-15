#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>

#define NUM_DICE 5
#define NUM_CATEGORIES 13

// Function prototypes
void roll_dice(int dice[]);
void display_dice(int dice[]);
int score_upper(int dice[], int number);
int score_three_of_a_kind(int dice[]);
int score_four_of_a_kind(int dice[]);
int score_full_house(int dice[]);
int score_small_straight(int dice[]);
int score_large_straight(int dice[]);
int score_yahtzee(int dice[]);
int score_chance(int dice[]);
void display_scoreboard(int player_scores[], int computer_scores[]);
void sort_dice(int dice[]);
int select_best_category(int dice[], int computer_scores[]);
void display_instructions(void);

int score_upper_ones(int dice[]) { return score_upper(dice, 1); }
int score_upper_twos(int dice[]) { return score_upper(dice, 2); }
int score_upper_threes(int dice[]) { return score_upper(dice, 3); }
int score_upper_fours(int dice[]) { return score_upper(dice, 4); }
int score_upper_fives(int dice[]) { return score_upper(dice, 5); }
int score_upper_sixes(int dice[]) { return score_upper(dice, 6); }

// Scoring functions array
int (*scoring_functions[NUM_CATEGORIES])(int dice[]) = {
    score_upper_ones, score_upper_twos, score_upper_threes,
    score_upper_fours, score_upper_fives, score_upper_sixes,
    score_three_of_a_kind, score_four_of_a_kind, score_full_house,
    score_small_straight, score_large_straight, score_yahtzee, score_chance};

const char *categories[] = {
    "Ones", "Twos", "Threes", "Fours", "Fives", "Sixes",
    "Three of a Kind", "Four of a Kind", "Full House",
    "Small Straight", "Large Straight", "Yahtzee", "Chance"};

// Roll all five dice
void roll_dice(int dice[]) {
    for (int i = 0; i < NUM_DICE; i++) {
        dice[i] = rand() % 6 + 1;
    }
}

// Display the dice values
void display_dice(int dice[]) {
    printf("Dice: ");
    for (int i = 0; i < NUM_DICE; i++) {
        printf("%d ", dice[i]);
    }
    printf("\n");
}

// Sort dice to help in checking for straights and groups
void sort_dice(int dice[]) {
    int temp;
    for (int i = 0; i < NUM_DICE - 1; i++) {
        for (int j = 0; j < NUM_DICE - i - 1; j++) {
            if (dice[j] > dice[j + 1]) {
                temp = dice[j];
                dice[j] = dice[j + 1];
                dice[j + 1] = temp;
            }
        }
    }
}

// Calculate score for upper section (Ones to Sixes)
int score_upper(int dice[], int number) {
    int score = 0;
    for (int i = 0; i < NUM_DICE; i++) {
        if (dice[i] == number)
            score += number;
    }
    return score;
}

// Check for Three of a Kind
int score_three_of_a_kind(int dice[]) {
    int counts[6] = {0};
    for (int i = 0; i < NUM_DICE; i++)
        counts[dice[i] - 1]++;
    
    for (int i = 0; i < 6; i++) {
        if (counts[i] >= 3) {
            int score = 0;
            for (int j = 0; j < NUM_DICE; j++)
                score += dice[j];
            return score;
        }
    }
    return 0;
}

// Check for Four of a Kind
int score_four_of_a_kind(int dice[]) {
    int counts[6] = {0};
    for (int i = 0; i < NUM_DICE; i++)
        counts[dice[i] - 1]++;
    
    for (int i = 0; i < 6; i++) {
        if (counts[i] >= 4) {
            int score = 0;
            for (int j = 0; j < NUM_DICE; j++)
                score += dice[j];
            return score;
        }
    }
    return 0;
}

// Check for Full House
int score_full_house(int dice[]) {
    int counts[6] = {0};
    bool has_three = false, has_two = false;
    
    for (int i = 0; i < NUM_DICE; i++)
        counts[dice[i] - 1]++;
    
    for (int i = 0; i < 6; i++) {
        if (counts[i] == 3)
            has_three = true;
        else if (counts[i] == 2)
            has_two = true;
    }
    
    return (has_three && has_two) ? 25 : 0;
}

// Check for Small Straight
int score_small_straight(int dice[]) {
    int sorted[NUM_DICE];
    for (int i = 0; i < NUM_DICE; i++)
        sorted[i] = dice[i];
    sort_dice(sorted);
    
    // Remove duplicates
    int unique[NUM_DICE];
    int unique_count = 0;
    unique[0] = sorted[0];
    unique_count = 1;
    
    for (int i = 1; i < NUM_DICE; i++) {
        if (sorted[i] != sorted[i-1]) {
            unique[unique_count] = sorted[i];
            unique_count++;
        }
    }
    
    // Check for sequence of 4
    int consecutive = 1;
    for (int i = 1; i < unique_count; i++) {
        if (unique[i] == unique[i-1] + 1)
            consecutive++;
        else
            consecutive = 1;
        
        if (consecutive >= 4)
            return 30;
    }
    return 0;
}

// Check for Large Straight
int score_large_straight(int dice[]) {
    int sorted[NUM_DICE];
    for (int i = 0; i < NUM_DICE; i++)
        sorted[i] = dice[i];
    sort_dice(sorted);
    
    for (int i = 1; i < NUM_DICE; i++) {
        if (sorted[i] != sorted[i-1] + 1)
            return 0;
    }
    return 40;
}

// Check for Yahtzee
int score_yahtzee(int dice[]) {
    for (int i = 1; i < NUM_DICE; i++) {
        if (dice[i] != dice[0])
            return 0;
    }
    return 50;
}

// Score for Chance
int score_chance(int dice[]) {
    int score = 0;
    for (int i = 0; i < NUM_DICE; i++)
        score += dice[i];
    return score;
}

// Add running total calculation function
int calculate_running_total(int scores[]) {
    int total = 0;
    for (int i = 0; i < NUM_CATEGORIES; i++) {
        if (scores[i] != -1) {
            total += scores[i];
        }
    }
    return total;
}

// Modified display_scoreboard function
void display_scoreboard(int player_scores[], int computer_scores[]) {
    printf("\n|------------------------------------------------------|\n");
    printf("||                   YAHTZEE SCORES                   ||\n");
    printf("||----------------------------------------------------||\n");
    printf("||     Category    ||    Player     ||     Computer   ||\n");
    printf("|------------------------------------------------------|\n");
    
    for (int i = 0; i < NUM_CATEGORIES; i++) {
        printf("|| %-15s || ", categories[i]);
        
        // Player score
        if (player_scores[i] == -1) {
            printf("     ---      ||");
        } else {
            printf("     %3d      ||", player_scores[i]);
        }
        
        // Computer score
        if (computer_scores[i] == -1) {
            printf("      ---       ||\n");
        } else {
            printf("      %3d       ||\n", computer_scores[i]);
        }
    }
    
    printf("||-----------------||---------------||----------------||\n");
    
    
    int player_total = calculate_running_total(player_scores);
    int computer_total = calculate_running_total(computer_scores);
    printf("||  Running Total  ||      %3d      ||      %3d       ||\n",
           player_total, computer_total);
    
    printf("||-----------------||---------------||----------------||\n");
}


// Computer selects the best category
int select_best_category(int dice[], int computer_scores[]) {
    int best_score = -1;
    int best_category = -1;

    
    for (int i = 0; i < NUM_CATEGORIES; i++) {
        if (computer_scores[i] == -1) {
            int score = scoring_functions[i](dice);
            if (score > best_score) {
                best_score = score;
                best_category = i;
            }
        }
    }

    
    if (best_category == -1) {
        for (int i = 0; i < NUM_CATEGORIES; i++) {
            if (computer_scores[i] == -1) {
                best_category = i;
                break;
            }
        }
    }

    return best_category;
}

void display_instructions(void) {
    printf("\n\n\t\tInstructions\n\n");
    printf("Starting the Game:\n");
    printf("\tThe game consists of 13 rounds, where each player (you and the\n");
    printf("\tcomputer) will take turns rolling five dice and choosing a scoring\n");
    printf("\tcategory. The goal is to achieve the highest score.\n\n");
    
    printf("Rolling the Dice:\n");
    printf("\tDice will automatically roll at the start of your turn.\n\n");
    
    printf("Rerolling Dice (Optional):\n");
    printf("\t* You can reroll some or all dice up to two times per turn\n");
    printf("\t* Type 'y' to reroll or 'n' to keep current dice\n");
    printf("\t* Specify which dice to reroll using positions 1-5\n\n");
    
    printf("Scoring Categories (1-13):\n");
    printf("\t1-6: Ones through Sixes (sum of specified number)\n");
    printf("\t7: Three of a Kind (sum of all dice)\n");
    printf("\t8: Four of a Kind (sum of all dice)\n");
    printf("\t9: Full House (25 points)\n");
    printf("\t10: Small Straight (30 points)\n");
    printf("\t11: Large Straight (40 points)\n");
    printf("\t12: Yahtzee (50 points)\n");
    printf("\t13: Chance (sum of all dice)\n\n");
    
    printf("Press Enter to start the game...");
    getchar();
}

    

// evaluate potential score for a category
int evaluate_potential_score(int dice[], int category) {
    if (category <= 5) {
        return score_upper(dice, category + 1);
    }
    return scoring_functions[category](dice);
}

//decide if computer should reroll
bool should_computer_reroll(int dice[], int computer_scores[], int* best_score, int* best_category) {
    
    *best_score = 0;
    *best_category = -1;
    
    for (int i = 0; i < NUM_CATEGORIES; i++) {
        if (computer_scores[i] == -1) {
            int score = evaluate_potential_score(dice, i);
            if (score > *best_score) {
                *best_score = score;
                *best_category = i;
            }
        }
    }
    
    // Reroll thresholds for different categories
    const int THRESHOLD_UPPER = 8;     // Minimum desired score for upper section
    const int THRESHOLD_THREE = 15;    // Minimum for three of a kind
    const int THRESHOLD_FOUR = 20;     // Minimum for four of a kind
    const int THRESHOLD_CHANCE = 18;   // Minimum for chance
    
    // If we have a Yahtzee, Large Straight, or Full House, keep it
    if (*best_score >= 25) {
        return false;
    }
    
    // Check if current roll is too low based on category
    if (*best_category <= 5 && *best_score < THRESHOLD_UPPER) {
        return true;
    }
    if (*best_category == 6 && *best_score < THRESHOLD_THREE) {
        return true;
    }
    if (*best_category == 7 && *best_score < THRESHOLD_FOUR) {
        return true;
    }
    if (*best_category == 12 && *best_score < THRESHOLD_CHANCE) {
        return true;
    }
    
    return false;
}

// decide which dice to reroll
void select_dice_to_reroll(int dice[], int* reroll_indices, int* num_rerolls, int target_value) {
    *num_rerolls = 0;
    int counts[6] = {0};
    
    // Count occurrences of each value
    for (int i = 0; i < NUM_DICE; i++) {
        counts[dice[i] - 1]++;
    }
    
    // Find most common value
    int max_count = 0;
    int most_common = 0;
    for (int i = 0; i < 6; i++) {
        if (counts[i] > max_count) {
            max_count = counts[i];
            most_common = i + 1;
        }
    }
    
    // If trying for upper section
    if (target_value > 0) {
        for (int i = 0; i < NUM_DICE; i++) {
            if (dice[i] != target_value) {
                reroll_indices[*num_rerolls] = i;
                (*num_rerolls)++;
            }
        }
    }
    // If trying for of-a-kind or full house
    else if (max_count >= 2) {
        for (int i = 0; i < NUM_DICE; i++) {
            if (dice[i] != most_common) {
                reroll_indices[*num_rerolls] = i;
                (*num_rerolls)++;
            }
        }
    }
    // If no good pattern, reroll everything except highest values
    else {
        for (int i = 0; i < NUM_DICE; i++) {
            if (dice[i] < 5) {
                reroll_indices[*num_rerolls] = i;
                (*num_rerolls)++;
            }
        }
    }
}


// computer's turn section with this:
void take_computer_turn(int dice[], int computer_scores[]) {
    printf("\nComputer's turn:\n");
    roll_dice(dice);
    display_dice(dice);
    
    // Up to 2 rerolls
    for (int reroll = 0; reroll < 2; reroll++) {
        int best_score, best_category;
        
        if (should_computer_reroll(dice, computer_scores, &best_score, &best_category)) {
            printf("Computer decides to reroll...\n");
            
            int reroll_indices[NUM_DICE];
            int num_rerolls;
            
            // Determine reroll strategy based on best available category
            int target_value = -1;
            if (best_category <= 5) {
                target_value = best_category + 1;
            }
            
            select_dice_to_reroll(dice, reroll_indices, &num_rerolls, target_value);
            
            // Perform the reroll
            for (int i = 0; i < num_rerolls; i++) {
                dice[reroll_indices[i]] = (rand() % 6) + 1;
            }
            
            display_dice(dice);
        } else {
            printf("Computer keeps current dice.\n");
            break;
        }
     
    }
    
    // Select final category
    int final_category = select_best_category(dice, computer_scores);
    computer_scores[final_category] = scoring_functions[final_category](dice);
    
    printf("Computer chose %s and scored %d points.\n", 
           categories[final_category], 
           computer_scores[final_category]);
}


        

int main(void) {
    srand((unsigned int)time(NULL));
    
    int player_scores[NUM_CATEGORIES];
    int computer_scores[NUM_CATEGORIES];
    int dice[NUM_DICE];
    char buffer;
    
    // Initialize scores
    for (int i = 0; i < NUM_CATEGORIES; i++) {
        player_scores[i] = -1;
        computer_scores[i] = -1;
    }
    
    display_instructions();
    
    // Main game loop
    for (int turn = 0; turn < NUM_CATEGORIES; turn++) {
        printf("\n-- Turn %d --\n", turn + 1);

        // Player's turn
        printf("Player's turn:\n");
        roll_dice(dice);
        display_dice(dice);
        

        // Allow up to two rerolls
        for (int reroll = 0; reroll < 2; reroll++) {
            printf("Do you want to reroll some dice? (y/n): ");
            scanf(" %c", &buffer);

            if (buffer == 'y' || buffer == 'Y') {
                int num_rerolls;
                printf("Enter number of dice to reroll (1-5): ");
                scanf("%d", &num_rerolls);
                
                if (num_rerolls > 0 && num_rerolls <= NUM_DICE) {
                    printf("Enter positions to reroll (1-5): ");
                    for (int i = 0; i < num_rerolls; i++) {
                        int pos;
                        scanf("%d", &pos);
                        if (pos >= 1 && pos <= NUM_DICE) {
                            dice[pos-1] = (rand() % 6) + 1;
                        }
                    }
                    display_dice(dice);
                }
            } else {
                break;
            }
        }

        // Category selection
        int category;
        do {
            printf("Choose a category (1-13): ");
            scanf("%d", &category);
            category--;  
            
            if (category < 0 || category >= NUM_CATEGORIES) {
                printf("Invalid category! Choose between 1 and 13.\n");
                continue;
            }
            
            if (player_scores[category] != -1) {
                printf("Category already used! Choose another.\n");
                continue;
            }
            
            break;
        } while (1);
        
        player_scores[category] = scoring_functions[category](dice);
        take_computer_turn(dice, computer_scores);

        printf("\nAfter computer's turn:\n");
        display_scoreboard(player_scores, computer_scores);
        printf("\nPress Enter to continue to next round...");
        while (getchar() != '\n'); // Clear input buffer
        getchar();
    }

    // Calculate final scores
    int player_total = 0, computer_total = 0;
    for (int i = 0; i < NUM_CATEGORIES; i++) {
        player_total += (player_scores[i] == -1) ? 0 : player_scores[i];
        computer_total += (computer_scores[i] == -1) ? 0 : computer_scores[i];
    }

    // Display final results
    printf("\n=== Final Results ===\n");
    printf("Player Total: %d\n", player_total);
    printf("Computer Total: %d\n", computer_total);
    
    if (player_total > computer_total)
        printf("\nCongratulations! You win!\n");
    else if (computer_total > player_total)
        printf("\nComputer wins! Better luck next time!\n");
    else
        printf("\nIt's a tie!\n");

    return 0;
}
