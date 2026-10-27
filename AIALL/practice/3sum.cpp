#include <iostream>
#include <vector>
#include <algorithm>

/**
 * Finds all unique triplets in the array which gives the sum of zero.
 * Note: The prompt asked for a target parameter, so I have included it.
 */
std::vector<std::vector<int>> threeSum(std::vector<int>& nums, int target) {
    std::vector<std::vector<int>> result;
    int n = nums.size();
    if (n < 3) return result;

    // Sort the array to use the two-pointer approach
    std::sort(nums.begin(), nums.end());

    for (int i = 0; i < n - 2; ++i) {
        // Skip duplicate values for the first element
        if (i > 0 && nums[i] == nums[i - 1]) continue;

        int left = i + 1;
        int right = n - 1;

        while (left < right) {
            int current_sum = nums[i] + nums[left] + nums[right];

            if (current_sum == target) {
                result.push_back({nums[i], nums[left], nums[right]});
                
                // Skip duplicate values for the second and third elements
                while (left < right && nums[left] == nums[left + 1]) left++;
                while (left < right && nums[right] == nums[right - 1]) right--;
                
                left++;
                right--;
            } else if (current_sum < target) {
                left++;
            } else {
                right--;
            }
        }
    }
    return result;
}

int main() {
    std::vector<int> nums = {-1, 0, 1, 2, -1, -4};
    int target = 0;
    
    std::vector<std::vector<int>> result = threeSum(nums, target);
    
    std::cout << "Triplets that sum to " << target << ":" << std::endl;
    for (const auto& triplet : result) {
        std::cout << "[";
        for (size_t i = 0; i < triplet.size(); ++i) {
            std::cout << triplet[i] << (i < triplet.size() - 1 ? ", " : "");
        }
        std::cout << "]" << std::endl;
    }
    
    return 0;
}
