#ifndef LIB_PIXEL_MATH_H_
#define  LIB_PIXEL_MATH_H_

#include <vector>

namespace hipscat{

std::vector<std::vector<long long int> > generate_alignment(
    const std::vector<long long int> &histogram,
    short highest_order,
    short lowest_order,
    long long int threshold
);

}

#endif