SUBJECTS_DATA = [
    {
        "name": "Mathematics",
        "slug": "mathematics",
        "category": "Science",
        "icon": "calculator",
        "color": "#2563EB",
        "description": "Number Bases, Modular Arithmetic, Fractions, Indices, Logarithms, Sets, Surds, Polynomials, Variation, Algebraic Expressions, Linear/Quadratic/Simultaneous Equations, Inequalities, Matrices, Progressions, Binary Operations, Geometry, Trigonometry, Bearings, Coordinate Geometry, Loci, Calculus, Statistics, Probability -- complete WAEC/NECO/GCE/JAMB syllabus",
        "lessons": [
            {
                "title": "Number and Numeration",
                "slug": "number-and-numeration",
                "summary": "Number bases, modular arithmetic, fractions, decimals, percentages, indices, logarithms, surds, sets, polynomials, variation, ratios, financial arithmetic",
                "order_index": 1,
                "estimated_minutes": 240,
                "content": "<h2>Number and Numeration</h2><p>Welcome to the foundation of all mathematics -- numbers! Without a solid number sense, advanced math will always feel shaky. This chapter covers everything from number bases to financial arithmetic, building up step by step.</p>",
                "topics": [
                    {"title":"Number Bases","order_index":1,"content":"<h3>Number Bases</h3><p>We use 10 digits (0-9) because we have 10 fingers! A <b>number base</b> is how many unique digits we use. Base 2 (binary) uses 0,1 for computers. Base 16 (hex) uses 0-9,A-F for colors.</p><p><b>Any base to base 10:</b> Multiply each digit by base^position. 1011_2 = 1x8+0x4+1x2+1x1 = 11_10</p><p><b>Base 10 to any base:</b> Repeatedly divide, read remainders upward. 25_10 = 11001_2</p><p><b>Binary addition:</b> 1+1=10 (carry 1). 1011+111=10010</p><p><b>Practice:</b> 1) Convert 101101_2 to base 10. 2) Convert 156_10 to base 2, 8, 16. 3) Add 11011_2+10101_2.</p><p><b>Answers:</b> 1) 45. 2) 10011100_2, 234_8, 9C_16. 3) 110000_2=48.</p>"},
                    {"title":"Modular Arithmetic","order_index":2,"content":"<h3>Modular Arithmetic</h3><p>It's 10AM, meeting in 4 hours = 2PM. That's modulo 12! <b>a = b (mod m)</b> means a and b have same remainder when divided by m.</p><p><b>Examples:</b> 17 = 5 (mod 12), 23 = 2 (mod 7), 100 = 1 (mod 9).</p><p><b>Applications:</b> Clocks (mod 12), days of week (mod 7), even/odd (mod 2), RSA encryption, ISBN checksums.</p><p><b>Practice:</b> 1) Find 47 mod 6, 100 mod 9, 365 mod 7. 2) If today is Wednesday, what day in 100 days? 3) Compute 123x456 mod 11.</p><p><b>Answers:</b> 1) 5,1,1. 2) Friday (100=7x14+2). 3) 123=11x11+2, 456=11x41+5, 2x5=10 mod 11.</p>"},
                    {"title":"Fractions, Decimals and Percentages","order_index":3,"content":"<h3>Fractions, Decimals and Percentages</h3><p>Same thing in different languages! Chocolate bar: eat 25 squares = 1/4 = 0.25 = 25%.</p><p><b>Operations:</b> 1/3+1/4=7/12 (common denominator). 2/3x3/4=1/2. (2/3)/(3/4)=2/3x4/3=8/9.</p><p><b>Applications:</b> 15% of 200 = 30. % increase: N5000+10% = N5500. % change: (50/200)x100=25%.</p><p><b>Practice:</b> 1) A man spends 40% on food, 25% rent, 15% transport, saves N15,000. Salary? 2) Shopkeeper marks 30% above cost, gives 10% discount. Profit%?</p><p><b>Answers:</b> 1) N75,000. 2) 17%.</p>"},
                    {"title":"Indices and Laws of Indices","order_index":4,"content":"<h3>Indices (Exponents)</h3><p>2x2x2x2x2x2x2x2 = 2^8. An index tells us how many times to multiply.</p><p><b>7 Laws:</b> a^m x a^n = a^(m+n), a^m/a^n = a^(m-n), (a^m)^n = a^(mn), a^0=1, a^(-n)=1/a^n, a^(1/n)=nth root, (ab)^n=a^n b^n.</p><p><b>Equations:</b> 3^(x+2)=27^(2x-1) -> 3^(x+2)=3^(6x-3) -> x+2=6x-3 -> x=1.</p>"},
                    {"title":"Logarithms","order_index":5,"content":"<h3>Logarithms</h3><p>If 2^3=8, then log_2(8)=3. A logarithm answers: 'what power gives this number?'</p><p><b>4 Laws:</b> log(MN)=logM+logN, log(M/N)=logM-logN, log(M^k)=k logM, log_a(b)=log_c(b)/log_c(a).</p><p><b>Example:</b> log_2(8x4)=log_2(8)+log_2(4)=3+2=5. Check: 32=2^5 ok!</p><p><b>Practice:</b> If log_10(2)=0.3010, log_10(3)=0.4771, find log_10(6) and log_10(72/5).</p><p><b>Answers:</b> log6=0.7781. log(72/5)=1.1582.</p>"},
                    {"title":"Sets and Venn Diagrams","order_index":6,"content":"<h3>Sets and Venn Diagrams</h3><p>A set is a collection of distinct objects. Notation: A={1,2,3}, 2 in A, 5 not in A.</p><p><b>Operations:</b> Union (A U B): in A OR B. Intersection (A n B): in BOTH. Complement (A'): NOT in A.</p><p><b>Example:</b> 30 students: 18 like Math, 15 like English, 8 like both. Neither = 30-(10+7+8)=5.</p><p><b>Practice:</b> 1) A={primes<20}, B={evens<20}. Find A U B and A n B. 2) 45 students, 30 passed Math, 25 English, 12 both. Failed both?</p><p><b>Answers:</b> 1) A U B has 18 elements, A n B={2}. 2) 45-(30+25-12)=2.</p>"},
                    {"title":"Surds (Radicals)","order_index":7,"content":"<h3>Surds</h3><p>sqrt(2)=1.414... never ends. Keep sqrt() for exact value.</p><p><b>Rules:</b> sqrt(ab)=sqrt(a)xsqrt(b). sqrt(72)=sqrt(36x2)=6sqrt(2).</p><p><b>Rationalize:</b> 1/sqrt(2)=sqrt(2)/2. 1/(3+sqrt(2))=(3-sqrt(2))/7.</p><p><b>Challenge:</b> Which is larger: sqrt5+sqrt3 or sqrt6+sqrt2? Square both! 8+2sqrt15 vs 8+2sqrt12. sqrt5+sqrt3 is larger.</p>"},
                    {"title":"Polynomials","order_index":8,"content":"<h3>Polynomials</h3><p>3x^4+2x^2-5 is degree 4. Terms: 3x^4, 2x^2, -5. Coefficient: 3. Constant: -5.</p><p><b>Remainder Theorem:</b> P(x)/(x-a) remainder = P(a).</p><p><b>Factor Theorem:</b> If P(a)=0, (x-a) is a factor.</p><p><b>Example:</b> x^3-9x^2+26x-24. Since P(3)=0, (x-3) is factor. Divide: x^2-6x+8=(x-2)(x-4). So (x-3)(x-2)(x-4).</p>"},
                    {"title":"Variation","order_index":9,"content":"<h3>Variation</h3><p><b>Direct:</b> y=kx. Bigger pizza=bigger slice. <b>Inverse:</b> y=k/x. More friends=smaller slice.</p><p><b>Joint:</b> y=kxz. <b>Partial:</b> y=kx+c. Taxi: N200+N100/km=100d+200.</p><p><b>Example:</b> Electricity cost varies partly as units and partly fixed. 100u=N5000, 200u=N8000. C=aU+F -> a=N30/unit, F=N2000.</p>"},
                    {"title":"Financial Arithmetic","order_index":10,"content":"<h3>Financial Arithmetic</h3><p><b>Simple Interest:</b> I=PRT/100. P=principal, R=rate, T=time. <b>Compound Interest:</b> A=P(1+R/100)^n.</p><p><b>Example:</b> N10,000 at 5% for 2 years. Simple: I=10000x5x2/100=N1000. Compound: A=10000(1.05)^2=N11,025. Interest=N1,025.</p><p><b>Depreciation:</b> A=P(1-R/100)^n. Used for cars, equipment.</p>"}
                ]
            },
            {
                "title": "Algebra",
                "slug": "algebra",
                "summary": "Algebraic expressions, linear/quadratic equations, simultaneous equations, inequalities, matrices, progressions, binary operations",
                "order_index": 2,
                "estimated_minutes": 300,
                "content": "<h2>Algebra</h2><p>Algebra moves us from specific numbers to general relationships. Instead of '3+5=8', we solve 'x+y=z' for entire classes of problems.</p>",
                "topics": [
                    {"title":"Algebraic Expressions","order_index":1,"content":"<h3>Algebraic Expressions</h3><p>3x^2+5x-2 has: terms 3x^2,5x,-2; variable x; coefficients 3,5; constant -2.</p><p><b>Simplify:</b> 4x^2+3x-2x^2+5x-7=2x^2+8x-7. <b>Expand:</b> (x+3)(x+2)=x^2+5x+6 (FOIL).</p><p><b>Special:</b> (a+b)(a-b)=a^2-b^2. (a+b)^2=a^2+2ab+b^2.</p><p><b>Factorize:</b> 6x^2+9x=3x(2x+3). x^2+7x+12=(x+3)(x+4). x^2-9=(x+3)(x-3).</p>"},
                    {"title":"Linear Equations","order_index":2,"content":"<h3>Linear Equations</h3><p>Goal: isolate variable. Do same to both sides.</p><p><b>Simple:</b> 3x+7=22 -> 3x=15 -> x=5. <b>Both sides:</b> 5x-3=2x+9 -> 3x=12 -> x=4.</p><p><b>Fractions:</b> (x-2)/3+(x+1)/4=5. Multiply by 12: 4(x-2)+3(x+1)=60 -> 7x=65 -> x=65/7.</p><p><b>Word problem:</b> A father is 3x son's age. In 12 years, he'll be 2x. Son=12, Father=36.</p>"},
                    {"title":"Linear Inequalities","order_index":3,"content":"<h3>Linear Inequalities</h3><p>Same as equations but FLIP sign when multiplying/dividing by negative.</p><p><b>Examples:</b> 4x-7<9 -> x<4. 5-2x>=11 -> -2x>=6 -> x<=-3 (flipped!).</p><p><b>Double inequality:</b> -3<2x+1<7 -> -4<2x<6 -> -2<x<3.</p>"},
                    {"title":"Quadratic Equations","order_index":4,"content":"<h3>Quadratic Equations: ax^2+bx+c=0</h3><p><b>Factorization:</b> x^2+5x+6=0 -> (x+2)(x+3)=0 -> x=-2,-3.</p><p><b>Formula:</b> x=[-b +/- sqrt(b^2-4ac)]/2a. Always works!</p><p><b>Completing square:</b> x^2+6x+5=0 -> (x+3)^2=4 -> x=-1,-5.</p><p><b>Discriminant D=b^2-4ac:</b> D>0=2 roots, D=0=1 root, D<0=no real roots.</p><p><b>Sum of roots:</b> -b/a. <b>Product:</b> c/a.</p><p><b>Practice:</b> Find k so x^2-6x+k=0 has equal roots. D=0 -> 36-4k=0 -> k=9.</p>"},
                    {"title":"Simultaneous Equations","order_index":5,"content":"<h3>Simultaneous Equations</h3><p><b>Substitution:</b> y=2x+1, 3x+y=11 -> 3x+2x+1=11 -> x=2,y=5.</p><p><b>Elimination:</b> 2x+3y=13, 2x-y=1 -> subtract: 4y=12 -> y=3,x=2.</p><p><b>Non-linear:</b> y=x+2, y=x^2 -> x^2=x+2 -> x=2(y=4) or x=-1(y=1).</p><p><b>Word problem:</b> Two-digit number is 4x sum of digits. Reversed is 18 more. Number=24.</p>"},
                    {"title":"Matrices and Determinants","order_index":6,"content":"<h3>Matrices</h3><p>A matrix is a rectangular array of numbers. <b>Addition:</b> same size, add corresponding.</p><p><b>Multiplication:</b> rows x columns. NOT commutative (AB not= BA).</p><p><b>Determinant of 2x2:</b> det[a b;c d]=ad-bc. <b>Inverse:</b> A^-1=(1/det)[d -b;-c a].</p><p><b>Solving:</b> [a b;c d][x;y]=[e;f] -> [x;y]=A^-1[e;f].</p>"},
                    {"title":"Progressions (AP and GP)","order_index":7,"content":"<h3>Progressions</h3><p><b>AP:</b> constant difference d. T_n=a+(n-1)d. S_n=n/2[2a+(n-1)d].</p><p><b>GP:</b> constant ratio r. T_n=ar^(n-1). S_n=a(r^n-1)/(r-1). S_inf=a/(1-r) for |r|<1.</p><p><b>Practice:</b> Ball dropped from 100m, rebounds 4/5 of height. Total distance = 100+2(80+64+...)=100+2x400=900m.</p>"},
                    {"title":"Binary Operations","order_index":8,"content":"<h3>Binary Operations</h3><p>Properties: closure, commutativity, associativity, identity, inverse.</p><p><b>Example:</b> a*b=a+b-3. Identity: a*e=a+e-3=a -> e=3. Inverse of 5: 5*x=3 -> 5+x-3=3 -> x=1.</p>"}
                ]
            },
            {
                "title": "Geometry and Trigonometry",
                "slug": "geometry-and-trigonometry",
                "summary": "Angles, triangles, polygons, circles, circle theorems, trigonometric ratios, bearings, coordinate geometry, loci",
                "order_index": 3,
                "estimated_minutes": 240,
                "content": "<h2>Geometry and Trigonometry</h2><p>Geometry studies shapes. Trigonometry relates angles to side lengths. Together they let architects design buildings, engineers build bridges, and GPS locate you.</p>",
                "topics": [
                    {"title":"Angles, Triangles and Polygons","order_index":1,"content":"<h3>Angles and Triangles</h3><p><b>Types:</b> Acute(<90), Right(90), Obtuse(90-180), Straight(180), Reflex(180-360).</p><p><b>Parallel lines:</b> Alternate(Z) equal, Corresponding(F) equal, Interior supplementary(sum=180).</p><p><b>Triangles:</b> Sum=180. Pythagoras: a^2+b^2=c^2.</p><p><b>Polygons:</b> Sum interior=(n-2)x180. Each interior(regular)=(n-2)x180/n. Exterior=360/n.</p><p><b>Practice:</b> Regular polygon with interior 156. How many sides? (n-2)x180/n=156 -> 180n-360=156n -> n=15 sides.</p>"},
                    {"title":"Circles and Circle Theorems","order_index":2,"content":"<h3>Circles</h3><p><b>Parts:</b> Radius, diameter(d=2r), chord, arc, sector, tangent.</p><p><b>Formulas:</b> C=2pi r. A=pi r^2. Arc=theta/360x2pi r. Sector=theta/360xpi r^2.</p><p><b>7 Theorems:</b> (1) Center angle=2x circumference. (2) Angle in semicircle=90. (3) Same segment angles equal. (4) Cyclic quadrilateral opposite sum=180. (5) Alternate segment. (6) Radius perpendicular tangent. (7) Equal chords equidistant center.</p>"},
                    {"title":"Trigonometric Ratios","order_index":3,"content":"<h3>SOH CAH TOA</h3><p>sin=Opp/Hyp, cos=Adj/Hyp, tan=Opp/Adj. <b>Special angles:</b> 0,30,45,60,90. sin: 0,1/2,root2/2,root3/2,1.</p><p><b>Identity:</b> sin^2+cos^2=1. sin(90-?)=cos?.</p><p><b>Elevation/Depression:</b> Angle looking UP/DOWN.</p>"},
                    {"title":"Angles of Elevation and Depression","order_index":4,"content":"<h3>Elevation and Depression</h3><p><b>Example:</b> From 20m from tree, elevation to top=45. Height=20xtan45=20m.</p><p><b>Example:</b> From 50m tower, depression to car=30. Distance=50/tan30=50root3=86.6m.</p>"},
                    {"title":"Bearings","order_index":5,"content":"<h3>Bearings</h3><p>Measured clockwise from North, always 3 digits. N=000, NE=045, E=090, SE=135, S=180, SW=225, W=270, NW=315.</p><p><b>Example:</b> Ship sails 10km on bearing 060. East component=10xsin60=8.66km. North component=10xcos60=5km.</p>"},
                    {"title":"Coordinate Geometry","order_index":6,"content":"<h3>Coordinate Geometry</h3><p><b>Distance:</b> d=sqrt[(x2-x1)^2+(y2-y1)^2]. <b>Midpoint:</b> ((x1+x2)/2,(y1+y2)/2).</p><p><b>Gradient:</b> m=(y2-y1)/(x2-x1). <b>Line:</b> y-y1=m(x-x1) or y=mx+c.</p><p><b>Parallel:</b> same m. <b>Perpendicular:</b> m1xm2=-1.</p>"},
                    {"title":"Loci","order_index":7,"content":"<h3>Loci</h3><p>A locus is the set of all points satisfying a condition. Circle (fixed distance from point), Perpendicular bisector (equidistant from 2 points), Angle bisector (equidistant from 2 lines), Parallel lines (fixed distance from a line).</p>"}
                ]
            },
            {
                "title": "Introductory Calculus",
                "slug": "introductory-calculus",
                "summary": "Differentiation, integration, rates of change, gradients, stationary points, areas under curves",
                "order_index": 4,
                "estimated_minutes": 120,
                "content": "<h2>Introductory Calculus</h2><p>Calculus is the mathematics of change. Differentiation finds rates of change, integration finds areas and accumulations.</p>",
                "topics": [
                    {"title":"Differentiation","order_index":1,"content":"<h3>Differentiation</h3><p>If y=x^n, dy/dx=nx^(n-1). y=5x^2 -> dy/dx=10x. y=7 -> dy/dx=0.</p><p><b>Gradient at point:</b> Substitute x into dy/dx. y=x^2 at x=3: gradient=6.</p><p><b>Stationary points:</b> Set dy/dx=0. Max or min based on second derivative.</p><p><b>Applications:</b> Find max profit, min cost, velocity as derivative of displacement.</p>"},
                    {"title":"Integration","order_index":2,"content":"<h3>Integration</h3><p>Reverse of differentiation. Integral x^n dx = x^(n+1)/(n+1) + C.</p><p><b>Definite integral (area):</b> Integral_a^b f(x)dx = F(b)-F(a).</p><p><b>Example:</b> Area under y=x^2 from 0 to 2 = [x^3/3]_0^2 = 8/3 sq units.</p>"}
                ]
            },
            {
                "title": "Statistics and Probability",
                "slug": "statistics-and-probability",
                "summary": "Data representation, central tendency, dispersion, permutations, combinations, probability",
                "order_index": 5,
                "estimated_minutes": 120,
                "content": "<h2>Statistics and Probability</h2><p>Statistics organizes data. Probability measures likelihood. Together they help us make decisions under uncertainty.</p>",
                "topics": [
                    {"title":"Measures of Central Tendency","order_index":1,"content":"<h3>Mean, Median, Mode</h3><p><b>Mean:</b> Sum/count. <b>Median:</b> Middle when ordered. <b>Mode:</b> Most frequent.</p><p><b>Example:</b> 3,7,2,9,7,5. Mean=33/6=5.5. Ordered:2,3,5,7,7,9. Median=(5+7)/2=6. Mode=7.</p>"},
                    {"title":"Measures of Dispersion","order_index":2,"content":"<h3>Range, Variance, Std Deviation</h3><p><b>Range:</b> Largest-smallest. <b>Variance:</b> Avg of squared differences from mean. <b>Std dev:</b> sqrt(variance).</p><p><b>Example:</b> 4,6,8. Mean=6. Variance=[4+0+4]/3=8/3. Std dev=sqrt(8/3)=1.63.</p>"},
                    {"title":"Permutation and Combination","order_index":3,"content":"<h3>Permutation and Combination</h3><p><b>Permutation (order matters):</b> nPr=n!/(n-r)! <b>Combination (order doesn't):</b> nCr=n!/[r!(n-r)!]</p><p>Arrange=permutation. Choose=combination. 10P3=720 ways to arrange 3 from 10. 10C3=120 ways to choose 3 from 10.</p>"},
                    {"title":"Probability","order_index":4,"content":"<h3>Probability</h3><p>P(event)=favorable/total. Range: 0(impossible) to 1(certain).</p><p><b>Mutually exclusive:</b> P(A or B)=P(A)+P(B). <b>Independent:</b> P(A and B)=P(A)xP(B).</p><p><b>Example:</b> Coin P(H)=1/2. Dice P(4)=1/6. Cards P(Ace)=4/52=1/13.</p>"}
                ]
            }
        ]
    },
    {
        "name": "English Language",
        "slug": "english-language",
        "category": "General Studies",
        "icon": "book-open",
        "color": "#DC2626",
        "description": "Complete WAEC/NECO/GCE/JAMB English syllabus: Lexis, Structure, Oral English, Comprehension, Essay Writing, Summary, Literature-in-English. Based on Barrister Oscar Izeyor Iyoha's 'Fundamental Formulas of the English Language' approach -- error detection formulas, sentence construction patterns, and exam strategy formulas.",
        "lessons": [
            {
                "title": "Lexis and Structure",
                "slug": "lexis-and-structure",
                "summary": "Vocabulary, synonyms, antonyms, collocations, phrasal verbs, idioms, words in context, word formation, register, prefixes and suffixes",
                "order_index": 1,
                "estimated_minutes": 300,
                "content": "<h2>Lexis and Structure</h2><p>Your vocabulary is your toolbox. The richer your lexis, the more precisely you can express ideas. This chapter covers everything from everyday words to academic register.</p>",
                "topics": [
                    {"title":"Synonyms and Antonyms","order_index":1,"content":"<h3>Synonyms and Antonyms</h3><p><b>Synonyms</b> are words with similar meanings. <b>Antonyms</b> are opposites.</p><p>Abandon=desert/leave/resign/quit. Opposite: keep/retain/maintain.</p><p>Beautiful=gorgeous/stunning/magnificent. Opposite: ugly/hideous/grotesque.</p><p><b>Formula:</b> In JAMB/WAEC, look for precise synonyms -- not just close meanings but exact matches in context.</p>"},
                    {"title":"Collocations","order_index":2,"content":"<h3>Collocations</h3><p>Words that naturally go together. Make a decision (not do a decision). Heavy rain (not strong rain).</p><p><b>Types:</b> Adjective+Noun (strong coffee), Verb+Noun (commit a crime), Adverb+Adjective (highly unlikely).</p><p><b>Key collocations:</b> Catch a cold, break the news, save time, take a break, pay attention, tell a lie, make a noise.</p><p><b>Formula:</b> When unsure which word fits, think: 'What word is this word FRIENDS with?'</p>"},
                    {"title":"Phrasal Verbs","order_index":3,"content":"<h3>Phrasal Verbs</h3><p>Verb + preposition = completely different meaning!</p><p><b>Come:</b> Come across (find accidentally), come down (criticize), come up with (think of), come out (reveal), come round (visit/agree).</p><p><b>Get:</b> Get over (recover), get along (be friendly), get by (manage), get through (contact/survive), get at (imply).</p><p><b>Put:</b> Put off (postpone), put up with (tolerate), put across (communicate), put down (suppress/insult).</p><p><b>Formula:</b> The preposition CHANGES the meaning. Memorize phrasal verbs by the particle (up, down, off, on, out, over, through, across).</p>"},
                    {"title":"Idioms and Figurative Expressions","order_index":4,"content":"<h3>Idioms</h3><p>Idioms are fixed expressions where the meaning is NOT literal.</p><p>Bite the bullet=face pain bravely. Spill the beans=reveal secret. Break the ice=start conversation. Hit the nail on the head=exactly correct. Piece of cake=very easy. Once in a blue moon=rarely. Under the weather=ill. Beat around the bush=avoid direct topic.</p>"},
                    {"title":"Word Formation (Prefixes and Suffixes)","order_index":5,"content":"<h3>Word Formation</h3><p>Prefixes: un-(not), re-(again), pre-(before), mis-(wrongly), dis-(opposite), inter-(between).</p><p>Suffixes: -tion (noun), -ment (noun), -ly (adverb), -ful (adjective), -less (without), -able (can be).</p><p>Happy: unhappy, happiness, happily, unhappy. Care: careful, careless, carefully, carelessly, carelessness.</p><p><b>Formula:</b> Learn the most common 20 prefixes and 20 suffixes. They unlock 1000s of words.</p>"},
                    {"title":"Register (Language of Specific Fields)","order_index":6,"content":"<h3>Register</h3><p>Different fields use different words. Medicine: diagnosis, surgery, prescription. Law: plaintiff, defendant, verdict, appeal. Economics: demand, supply, inflation, recession. Religion: salvation, redemption, covenant, grace. Journalism: scoop, headline, editorial, column.</p><p><b>Formula:</b> Each profession has a distinct VOCABULARY SET. Match the word to the context.</p>"}
                ]
            },
            {
                "title": "Grammatical Structure",
                "slug": "grammatical-structure",
                "summary": "Parts of speech, tenses, concord, active/passive voice, direct/indirect speech, question tags, conditionals, clauses, punctuation, concord, subjunctive mood, articles, prepositions",
                "order_index": 2,
                "estimated_minutes": 360,
                "content": "<h2>Grammatical Structure</h2><p>Grammar is the FRAMEWORK that holds language together. Master these formulas and you'll never make a mistake in JAMB/WAEC use of English.</p>",
                "topics": [
                    {"title":"Parts of Speech","order_index":1,"content":"<h3>Parts of Speech</h3><p>8 parts: Noun (person/place/thing), Pronoun (replaces noun), Verb (action/state), Adjective (describes noun), Adverb (describes verb), Preposition (relationship), Conjunction (connects), Interjection (emotion).</p>"},
                    {"title":"Tenses (Complete Guide)","order_index":2,"content":"<h3>12 Tenses</h3><p><b>Present:</b> I eat, I am eating, I have eaten, I have been eating.</p><p><b>Past:</b> I ate, I was eating, I had eaten, I had been eating.</p><p><b>Future:</b> I will eat, I will be eating, I will have eaten, I will have been eating.</p><p><b>Formula:</b> 2 axes (time: past/present/future x aspect: simple/continuous/perfect/perfect continuous = 12).</p>"},
                    {"title":"Subject-Verb Agreement (Concord)","order_index":3,"content":"<h3>Concord</h3><p>Singular subject -> singular verb. Plural subject -> plural verb.</p><p>He goes (not go). They go (not goes). Each student has (not have). Either the teacher or the students are (verb agrees with nearest).</p><p><b>Formula:</b> The number of the subject (singular/plural) determines the verb. Watch for intervening phrases: 'The box of chocolates IS...' not 'are'.</p><p><b>Tricky words:</b> Everyone IS, Neither IS, The committee IS (group), Scissors ARE (always plural).</p>"},
                    {"title":"Active and Passive Voice","order_index":4,"content":"<h3>Active and Passive Voice</h3><p><b>Active:</b> Subject DOES action. 'The boy kicked the ball.'</p><p><b>Passive:</b> Subject RECEIVES action. 'The ball was kicked by the boy.'</p><p><b>Formula:</b> Passive = Be (in correct tense) + Past Participle. The passive object becomes active subject.</p><p>The teacher teaches (present active) -> The students are taught (present passive). Shakespeare wrote (past active) -> Was written by Shakespeare (past passive).</p>"},
                    {"title":"Direct and Indirect (Reported) Speech","order_index":5,"content":"<h3>Direct to Indirect Speech</h3><p><b>Formula:</b> Shift tense BACK one step. Present->Past, Past->Past Perfect, Will->Would, Can->Could, May->Might, Must->Had to.</p><p>Direct: She said, 'I am tired.' Indirect: She said that she was tired.</p><p>Direct: He said, 'I will call you.' Indirect: He said he would call me.</p><p><b>Pronouns:</b> Change according to the speaker's perspective.</p>"},
                    {"title":"Question Tags","order_index":6,"content":"<h3>Question Tags</h3><p><b>Formula:</b> Positive statement + Negative tag. Negative statement + Positive tag. Auxiliary verb + pronoun.</p><p>You are coming, aren't you? She isn't here, is she? He likes coffee, doesn't he? They didn't go, did they?</p><p><b>Exceptions:</b> I am, aren't I? Let's go, shall we? Open the door, will you?</p>"},
                    {"title":"Conditionals (If Clauses)","order_index":7,"content":"<h3>Conditionals</h3><p><b>Zero:</b> If+present, present (general truth). If you heat ice, it melts.</p><p><b>Type 1:</b> If+present, will+verb (real future). If it rains, I will stay.</p><p><b>Type 2:</b> If+past, would+verb (unreal present). If I were rich, I would travel.</p><p><b>Type 3:</b> If+had+pp, would+have+pp (unreal past). If I had studied, I would have passed.</p>"},
                    {"title":"Articles (A, An, The)","order_index":8,"content":"<h3>Articles</h3><p><b>Indefinite (a/an):</b> Non-specific. 'A book' (any book). 'An apple' (before vowel sound).</p><p><b>Definite (the):</b> Specific or known. 'The book on the table.' 'The sun.'</p><p><b>Zero article (no article):</b> General plurals (Cats are animals), proper nouns (Nigeria), meals (Breakfast is ready).</p>"},
                    {"title":"Prepositions","order_index":9,"content":"<h3>Prepositions</h3><p><b>Time:</b> AT (specific time/place), IN (month/year/morning), ON (day/date/street). At 5pm, in June, on Monday.</p><p><b>Place:</b> AT (point/building), IN (enclosed area), ON (surface). At school, in the room, on the table.</p><p><b>Common prep+noun:</b> By accident, on purpose, in danger, at war, on holiday, under pressure, out of order.</p>"},
                    {"title":"Clauses and Sentence Types","order_index":10,"content":"<h3>Clauses</h3><p><b>Independent:</b> Can stand alone. 'I went home.'</p><p><b>Dependent:</b> Needs main clause. 'Because I was tired, (I went home).'</p><p><b>Relative clauses:</b> Who/which/that/whom/whose. 'The man who called is here.'</p>"},
                    {"title":"Subjunctive Mood","order_index":11,"content":"<h3>Subjunctive Mood</h3><p>Used for wishes, demands, suggestions. Always use base verb (no -s).</p><p>I wish I WERE there (not was). I demand that he GO now (not goes). It is essential that she BE present (not is).</p>"}
                ]
            },
            {
                "title": "Oral English (Phonetics)",
                "slug": "oral-english",
                "summary": "Vowels, consonants, stress, intonation, rhyme, homophones, oddity identification",
                "order_index": 3,
                "estimated_minutes": 240,
                "content": "<h2>Oral English</h2><p>JAMB/WAEC tests your ability to hear and produce correct English sounds. Master the 44 phonemes of English.</p>",
                "topics": [
                    {"title":"Vowel Sounds","order_index":1,"content":"<h3>Vowel Sounds</h3><p>English has 12 pure vowels and 8 diphthongs. <b>Short vowels:</b> /i/ (bit), /e/ (bet), /ae/ (bat), /o/ (pot), /u/ (put), /o/ (about).</p><p><b>Long vowels:</b> /i:/ (beat), /a:/ (father), /o:/ (port), /u:/ (boot), /3:/ (bird).</p><p><b>8 Diphthongs:</b> /ei/ (bay), /ai/ (buy), /oi/ (boy), /au/ (now), /ou/ (go), /ie/ (ear), /ee/ (air), /ue/ (poor).</p>"},
                    {"title":"Consonant Sounds","order_index":2,"content":"<h3>Consonant Sounds</h3><p>24 consonant sounds. <b>Voiced vs voiceless:</b> /b/-/p/, /d/-/t/, /g/-/k/, /z/-/s/, /v/-/f/, /th/-/TH/.</p><p><b>Nasals:</b> /m/, /n/, /ng/. <b>Liquid:</b> /l/, /r/. <b>Glides:</b> /w/, /j/ (yes).</p><p><b>Tricky pairs:</b> Sheep (i:) / Ship (i). Full (u) / Fool (u:). Thin (voiceless th) / Then (voiced th).</p>"},
                    {"title":"Stress and Intonation","order_index":3,"content":"<h3>Stress and Intonation</h3><p><b>Word stress:</b> PREsent (noun) vs preSENT (verb). REcord (noun) vs reCORD (verb).</p><p><b>Syllable:</b> phoTOgraphy (4 syllables, stress on 2nd). eduCAtion (4 syllables, stress on 3rd).</p><p><b>Sentence stress:</b> Content words (nouns, verbs, adjectives) are stressed; function words (the, a, of) are weak.</p>"},
                    {"title":"Homophones and Rhymes","order_index":4,"content":"<h3>Homophones and Rhymes</h3><p><b>Homophones</b> sound the same but differ in meaning/spelling: wear/where, there/their/they're, write/right, heard/herd, see/sea, buy/by, pair/pear, hole/whole.</p><p><b>Rhymes:</b> Words with same final sound. Test: Pick the ODD one out (which word doesn't rhyme?).</p>"},
                    {"title":"Oddity Identification","order_index":5,"content":"<h3>Oddity Identification</h3><p>JAMB/WAEC classic: Which word has a DIFFERENT vowel/consonant sound? Which has different stress pattern?</p><p><b>Strategy:</b> Say all options aloud. Identify the sound in question. Compare each word <b>carefully</b>.</p>"}
                ]
            },
            {
                "title": "Comprehension and Summary",
                "slug": "comprehension-and-summary",
                "summary": "Reading comprehension passages, vocabulary in context, inference, main ideas, summary writing techniques",
                "order_index": 4,
                "estimated_minutes": 240,
                "content": "<h2>Comprehension and Summary</h2><p>Reading is extracting meaning from text. These skills are tested in EVERY JAMB/WAEC exam.</p>",
                "topics": [
                    {"title":"Reading Comprehension","order_index":1,"content":"<h3>Reading Comprehension</h3><p><b>Main idea:</b> What is the passage about overall? Usually in first sentence or last.</p><p><b>Vocabulary in context:</b> Never guess from isolation. Read SENTENCE around the word.</p><p><b>Inference:</b> Read between the lines. What does the author IMPLY?</p><p><b>Attitude/Tone:</b> Critical? Supportive? Neutral? Sarcastic? Look for emotional words.</p>"},
                    {"title":"Summary Writing","order_index":2,"content":"<h3>Summary Writing</h3><p><b>Formula:</b> (1) Read passage. (2) Identify key points. (3) Omit examples/details/repetition. (4) Use your OWN words. (5) Stay within word limit. (6) Write in complete sentences.</p><p><b>Common mistakes:</b> Copying verbatim, including examples, missing one key point, exceeding word limit.</p>"}
                ]
            },
            {
                "title": "Essay Writing",
                "slug": "essay-writing",
                "summary": "Formal letter, informal letter, article writing, speech writing, narrative, descriptive, argumentative, expository essays",
                "order_index": 5,
                "estimated_minutes": 300,
                "content": "<h2>Essay Writing</h2><p>You MUST write one essay in WAEC/JAMB. Structure and expression matter as much as content.</p>",
                "topics": [
                    {"title":"Letter Writing (Formal and Informal)","order_index":1,"content":"<h3>Letter Writing</h3><p><b>Formal letter format:</b> 6 parts: (1) Writer's address (2) Date (3) Recipient's address (4) Salutation (Sir/Dear Sir) (5) Subject line (bold/underline) (6) Body with introduction-body-conclusion (7) Subscription (Yours faithfully) (8) Signature & name.</p><p><b>Informal letter:</b> (1) Writer's address (2) Date (3) Salutation (Dear Uncle) (4) Body -- friendly tone (5) Subscription (Yours sincerely/Love) (6) Name.</p>"},
                    {"title":"Article Writing","order_index":2,"content":"<h3>Article Writing</h3><p>Title, byline (By...), Introduction (hook), Body (2-3 paragraphs with subheadings), Conclusion (call to action/strong finish).</p>"},
                    {"title":"Speech Writing","order_index":3,"content":"<h3>Speech</h3><p>Opening salutation, warm greeting, establish connection, clear message body, memorable conclusion, applause line.</p>"},
                    {"title":"Narrative and Descriptive Essays","order_index":4,"content":"<h3>Narrative/Descriptive</h3><p><b>Narrative:</b> Tell a story. Beginning, conflict, climax, resolution. Use chronological order. Engage senses.</p><p><b>Descriptive:</b> Paint a picture. Use vivid adjectives, metaphors, similes. Engage ALL 5 senses.</p>"},
                    {"title":"Argumentative and Expository Essays","order_index":5,"content":"<h3>Argumentative/Expository</h3><p><b>Argumentative:</b> Pick a side. Thesis, 3 arguments for, 2 counter-arguments (refuted), strong conclusion.</p><p><b>Expository:</b> Explain/analyze. No need to persuade. Clear structure with definitions, examples, analysis.</p>"}
                ]
            },
            {
                "title": "Literature-in-English",
                "slug": "literature-in-english",
                "summary": "Prose, poetry, drama, figures of speech, literary appreciation",
                "order_index": 6,
                "estimated_minutes": 240,
                "content": "<h2>Literature-in-English</h2><p>Literary appreciation tests your ability to understand and analyze creative works.</p>",
                "topics": [
                    {"title":"Prose and Drama","order_index":1,"content":"<h3>Prose and Drama</h3><p><b>Elements:</b> Plot, character, setting, theme, point of view, conflict, dialogue. <b>Characterization:</b> Protagonist, antagonist, round/flat, static/dynamic.</p><p><b>Drama terms:</b> Act, scene, soliloquy, aside, stage direction, tragedy, comedy, tragicomedy.</p>"},
                    {"title":"Poetry","order_index":2,"content":"<h3>Poetry</h3><p><b>Types:</b> Lyric, narrative, sonnet, ode, elegy, ballad. <b>Rhyme scheme:</b> ABAB, AABB, etc.</p><p><b>Meter:</b> Pattern of stressed/unstressed syllables. Iambic pentameter (da-DUM x5).</p>"},
                    {"title":"Figures of Speech","order_index":3,"content":"<h3>Figures of Speech</h3><p><b>Simile:</b> 'like' or 'as'. <b>Metaphor:</b> direct comparison. <b>Personification:</b> human qualities to objects. <b>Hyperbole:</b> exaggeration. <b>Irony:</b> opposite of literal. <b>Alliteration:</b> same initial sound. <b>Assonance:</b> repeated vowel sounds.</p>"},
                    {"title":"General Literary Appreciation","order_index":4,"content":"<h3>Literary Appreciation</h3><p><b>Questions test:</b> Theme, tone, mood, diction, imagery, symbolism, narrative technique. Always read the excerpt carefully before answering. Look for author's PURPOSE.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Physics",
        "slug": "physics",
        "category": "Science",
        "icon": "atom",
        "color": "#7C3AED",
        "description": "Complete WAEC/NECO/GCE/JAMB Physics syllabus: Motion, Forces, Energy, Waves, Light, Sound, Electricity, Magnetism, Electronics, Atomic Physics. Every topic with real-world analogies and step-by-step explanations from fundamentals to exam-level problems.",
        "lessons": [
            {
                "title": "Motion and Mechanics",
                "slug": "motion-and-mechanics",
                "summary": "Speed, velocity, acceleration, equations of motion, scalars and vectors, projectiles, circular motion, simple harmonic motion",
                "order_index": 1,
                "estimated_minutes": 360,
                "content": "<h2>Motion and Mechanics</h2><p>Everything moves! From a falling mango to a car braking, from Earth orbiting the Sun to an electron in a wire -- mechanics describes it all.</p>",
                "topics": [
                    {"title":"Scalars and Vectors","order_index":1,"content":"<h3>Scalars and Vectors</h3><p><b>Scalars</b> have only magnitude (size). Examples: speed (10 m/s), mass (5 kg), temperature (30 C).</p><p><b>Vectors</b> have magnitude AND direction. Examples: velocity (10 m/s north), force (5 N right), displacement (20 m east).</p><p><b>Vector addition:</b> Use tip-to-tail method. For perpendicular vectors: resultant = sqrt(a^2+b^2), direction = tan^-1(b/a).</p><p><b>Example:</b> Walk 3m east, then 4m north. Resultant displacement = sqrt(9+16)=5m at tan^-1(4/3)=53 degrees north of east.</p>"},
                    {"title":"Speed, Velocity and Acceleration","order_index":2,"content":"<h3>Speed, Velocity and Acceleration</h3><p><b>Speed = distance/time.</b> <b>Velocity = displacement/time.</b> <b>Acceleration = change in velocity/time.</b></p><p><b>Key insight:</b> Speed is scalar, velocity is vector. You can have constant speed but changing velocity (like circular motion).</p><p><b>Example:</b> Car travels 100km in 2 hr. Average speed=50 km/hr. If half was at 60 and half at 40, not simply average of speeds.</p>"},
                    {"title":"Equations of Linear Motion","order_index":3,"content":"<h3>SUVAT Equations</h3><p>Use when acceleration is CONSTANT.</p><p>v=u+at, s=ut+0.5at^2, v^2=u^2+2as, s=(u+v)t/2</p><p><b>Example:</b> Dropped stone from 45m. u=0, a=10, s=45. Using s=ut+0.5at^2: 45=5t^2 -> t=3s. Using v^2=u^2+2as: v^2=2x10x45=900 -> v=30 m/s.</p>"},
                    {"title":"Projectile Motion","order_index":4,"content":"<h3>Projectiles</h3><p>Objects launched at an angle. <b>Key:</b> Horizontal velocity is CONSTANT. Vertical motion follows SUVAT with g.</p><p><b>Time of flight:</b> T=2u sin(theta)/g. <b>Maximum height:</b> H=u^2 sin^2(theta)/2g. <b>Range:</b> R=u^2 sin(2theta)/g.</p><p><b>Maximum range:</b> at 45 degrees. Maximum height: at 90 degrees.</p>"},
                    {"title":"Simple Harmonic Motion","order_index":5,"content":"<h3>Simple Harmonic Motion</h3><p>Repetitive to-and-fro motion. Pendulum, spring-mass system.</p><p><b>Conditions:</b> Acceleration proportional to displacement, directed towards equilibrium. a = -w^2 x.</p><p><b>Period:</b> T=2pi sqrt(L/g) for pendulum. T=2pi sqrt(m/k) for spring. T is INDEPENDENT of amplitude!</p><p><b>Energy:</b> Swings between kinetic and potential. Total energy = 0.5kA^2.</p>"},
                    {"title":"Circular Motion","order_index":6,"content":"<h3>Circular Motion</h3><p><b>Angular velocity</b> w = theta/t = 2pi/T. <b>Centripetal acceleration:</b> a=v^2/r=w^2 r. <b>Centripetal force:</b> F=mv^2/r.</p><p><b>Examples:</b> Car rounding a curve (friction = centripetal force). Satellites in orbit (gravity = centripetal force).</p>"}
                ]
            },
            {
                "title": "Forces and Energy",
                "slug": "forces-and-energy",
                "summary": "Newton's laws, friction, equilibrium, work, energy, power, machines, momentum, impulse, pressure, buoyancy",
                "order_index": 2,
                "estimated_minutes": 360,
                "content": "<h2>Forces and Energy</h2><p>Forces push, pull, twist. Energy is the capacity to do work. These concepts unify all of physics.</p>",
                "topics": [
                    {"title":"Newton's Laws of Motion","order_index":1,"content":"<h3>Three Laws</h3><p><b>1st Law (Inertia):</b> Objects keep doing what they're doing unless a force acts.</p><p><b>2nd Law:</b> F=ma. Force = mass x acceleration.</p><p><b>3rd Law:</b> Action = Reaction. Every force has equal opposite pair.</p><p><b>Example:</b> 1000kg car accelerates at 2 m/s^2. Force = 1000x2=2000 N.</p>"},
                    {"title":"Friction","order_index":2,"content":"<h3>Friction</h3><p>Force that opposes motion. <b>Needed</b> for walking, driving, holding objects. <b>Wanted to reduce</b> in machines.</p><p><b>Static friction:</b> Bigger, acts before motion. <b>Kinetic friction:</b> Smaller, acts during motion.</p><p><b>Formula:</b> F=mu N. mu = coefficient of friction, N = normal reaction.</p>"},
                    {"title":"Work, Energy and Power","order_index":3,"content":"<h3>Work, Energy, Power</h3><p><b>Work:</b> W=Fd cos(theta). Unit: Joule. <b>Energy:</b> KE=0.5mv^2, GPE=mgh, EPE=0.5kx^2.</p><p><b>Power:</b> P=W/t=Fv. Unit: Watt (1 J/s).</p><p><b>Conservation of Energy:</b> Energy cannot be created/destroyed, only converted.</p><p><b>Example:</b> 2kg mass dropped from 10m. GPE=2x10x10=200J. Speed at ground: 0.5x2xv^2=200 -> v=14.1 m/s.</p>"},
                    {"title":"Momentum and Impulse","order_index":4,"content":"<h3>Momentum and Impulse</h3><p><b>Momentum:</b> p=mv (kg m/s). <b>Impulse:</b> Fxt=change in momentum = mv-mu.</p><p><b>Conservation:</b> In collisions, total momentum BEFORE = total AFTER.</p><p><b>Elastic collision:</b> KE conserved. <b>Inelastic:</b> KE not conserved (objects stick).</p>"},
                    {"title":"Pressure and Buoyancy","order_index":5,"content":"<h3>Pressure and Buoyancy</h3><p><b>Pressure:</b> P=F/A (Pascal = N/m^2). <b>Liquid pressure:</b> P=pgh. <b>Atmospheric pressure:</b> 1 atm=101,325 Pa.</p><p><b>Archimedes:</b> Buoyant force = weight of displaced fluid. <b>Upthrust:</b> Object floats if density less than fluid.</p>"},
                    {"title":"Simple Machines","order_index":6,"content":"<h3>Simple Machines</h3><p><b>MA = Load/Effort.</b> Levers, pulleys, inclined plane, screw, wedge, wheel and axle.</p><p><b>Efficiency = (Work output/Work input)x100%.</b> Energy loss due to friction.</p>"}
                ]
            },
            {
                "title": "Waves, Light and Sound",
                "slug": "waves-light-and-sound",
                "summary": "Types of waves, wave equations, reflection, refraction, diffraction, interference, lenses, mirrors, optical instruments, sound waves",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Waves, Light and Sound</h2><p>Waves carry energy without transporting matter. Light is electromagnetic. Sound is mechanical. Both exhibit wave behavior.</p>",
                "topics": [
                    {"title":"Types of Waves","order_index":1,"content":"<h3>Wave Types</h3><p><b>Transverse:</b> Particles vibrate perpendicular to direction. Example: light, water waves, string waves.</p><p><b>Longitudinal:</b> Particles vibrate parallel. Example: sound, compression waves in springs.</p><p><b>Progressive:</b> Carries energy forward. <b>Stationary:</b> Formed by superposition of two waves.</p>"},
                    {"title":"Wave Properties and Equations","order_index":2,"content":"<h3>Wave Characteristics</h3><p><b>v = f x lambda.</b> Velocity = frequency x wavelength.</p><p><b>Amplitude:</b> Maximum displacement from equilibrium. <b>Period:</b> T=1/f.</p><p><b>Properties:</b> Reflection, refraction, diffraction, interference, polarization.</p>"},
                    {"title":"Reflection and Refraction of Light","order_index":3,"content":"<h3>Reflection and Refraction</h3><p><b>Reflection:</b> Angle of incidence = angle of reflection. Plane mirrors, curved mirrors.</p><p><b>Refraction:</b> Bending of light when changing medium. <b>Snell's law:</b> n1 sin theta1 = n2 sin theta2.</p><p><b>Refractive index:</b> n = speed in vacuum/speed in medium = sin i/sin r.</p><p><b>Critical angle:</b> When angle of refraction = 90. sin C = 1/n. Used in fiber optics.</p>"},
                    {"title":"Lenses and Optical Instruments","order_index":4,"content":"<h3>Lenses</h3><p><b>Convex (converging):</b> Thick in middle, brings rays together. <b>Concave (diverging):</b> Thin in middle, spreads rays.</p><p><b>Lens formula:</b> 1/f = 1/u + 1/v. <b>Magnification:</b> M = v/u.</p><p><b>Optical instruments:</b> Microscope, telescope, periscope, camera, projector.</p>"},
                    {"title":"Sound Waves","order_index":5,"content":"<h3>Sound</h3><p>Longitudinal mechanical wave. Needs medium. Speed in air ~330 m/s. In water ~1500 m/s.</p><p><b>Loudness:</b> Depends on amplitude. <b>Pitch:</b> Depends on frequency. <b>Quality:</b> Depends on waveform.</p><p><b>Echo:</b> Reflection of sound. <b>Reverberation:</b> Multiple reflections.</p>"},
                    {"title":"Dispersion and Color","order_index":6,"content":"<h3>Dispersion</h3><p>Splitting white light into colors (ROYGBIV). Rainbow formation. Primary colors: Red, Green, Blue (additive). Cyan, Magenta, Yellow (subtractive).</p>"}
                ]
            },
            {
                "title": "Electricity and Magnetism",
                "slug": "electricity-and-magnetism",
                "summary": "Electrostatics, capacitors, current electricity, Ohm's law, circuits, resistors, cells, magnetic fields, electromagnets, electromagnetic induction, AC/DC",
                "order_index": 4,
                "estimated_minutes": 360,
                "content": "<h2>Electricity and Magnetism</h2><p>From lightning to phone chargers, electricity powers our world. Magnetism is intimately connected -- they are two sides of the same coin.</p>",
                "topics": [
                    {"title":"Electrostatics","order_index":1,"content":"<h3>Electrostatics</h3><p>Charges: like repel, unlike attract. <b>Coulomb's law:</b> F = kQ1Q2/r^2.</p><p><b>Electric field:</b> E = F/q = V/d. <b>Potential:</b> V = W/q (work per unit charge).</p><p><b>Earthing:</b> Neutralizing charge by connecting to ground.</p>"},
                    {"title":"Capacitors","order_index":2,"content":"<h3>Capacitors</h3><p>Store charge. <b>Q=CV.</b> Unit: Farad.</p><p><b>Series:</b> 1/C_total = 1/C1+1/C2+... <b>Parallel:</b> C_total = C1+C2+...</p><p><b>Energy:</b> E=0.5CV^2 stored in electric field.</p>"},
                    {"title":"Current Electricity","order_index":3,"content":"<h3>Current Electricity</h3><p><b>Current: I=Q/t</b> (Ampere). <b>Ohm's law:</b> V=IR (Volt = Ampere x Ohm).</p><p><b>Resistance:</b> R=pL/A (rho=resistivity, L=length, A=area). Temperature affects resistance.</p><p><b>Resistors in series:</b> R_total=R1+R2+R3. Same current, voltage divides. <b>Parallel:</b> 1/R=1/R1+1/R2+1/R3. Same voltage, current divides.</p>"},
                    {"title":"Electrical Energy and Power","order_index":4,"content":"<h3>Electrical Power</h3><p><b>P=IV=I^2R=V^2/R.</b> Energy consumed = Pxt = IVt. Kilowatt-hour (kWh) is commercial unit.</p><p><b>Example:</b> 60W bulb for 5 hours: Energy=60x5x3600=1,080,000 J = 0.3 kWh. Cost at N20/kWh = N6.</p>"},
                    {"title":"Cells and Emf","order_index":5,"content":"<h3>Cells and Electromotive Force</h3><p><b>Emf (E):</b> Total energy per charge from cell. <b>Terminal voltage:</b> V=E-Ir (r=internal resistance).</p><p><b>Cells in series:</b> E_total=E1+E2, r_total=r1+r2. <b>Parallel:</b> E_total=E, 1/r_total=1/r1+1/r2.</p>"},
                    {"title":"Magnetic Fields","order_index":6,"content":"<h3>Magnetic Fields</h3><p>Magnetic field lines: North to South (outside magnet). Field strength B (Tesla).</p><p><b>Force on current:</b> F=BIL sin(theta). <b>Force on moving charge:</b> F=Bqv (Lorentz force).</p><p><b>Right-hand rule:</b> Thumb=current, fingers=field, palm=force.</p>"},
                    {"title":"Electromagnetic Induction","order_index":7,"content":"<h3>Induction</h3><p><b>Faraday's law:</b> Induced emf = -N(dphi/dt). <b>Lenz's law:</b> Induced current opposes change.</p><p><b>Transformer:</b> Vp/Vs = Np/Ns. Step-up (increase voltage), step-down (decrease).</p><p><b>Power transmission:</b> High voltage reduces I^2R losses.</p>"}
                ]
            },
            {
                "title": "Modern Physics",
                "slug": "modern-physics",
                "summary": "Atomic structure, radioactivity, nuclear reactions, photoelectric effect, x-rays, semiconductors, electronics",
                "order_index": 5,
                "estimated_minutes": 240,
                "content": "<h2>Modern Physics</h2><p>Beyond everyday experience lies the strange world of atoms, nuclei, and quantum effects.</p>",
                "topics": [
                    {"title":"Atomic Structure","order_index":1,"content":"<h3>Atomic Structure</h3><p><b>Rutherford model:</b> Dense positive nucleus, electrons orbit. <b>Bohr model:</b> Electrons in fixed energy levels.</p><p><b>Proton:</b> +1 charge, mass 1. <b>Neutron:</b> 0 charge, mass 1. <b>Electron:</b> -1 charge, mass ~1/1840.</p><p><b>Atomic number Z:</b> Number of protons. <b>Mass number A:</b> Protons+neutrons.</p>"},
                    {"title":"Radioactivity","order_index":2,"content":"<h3>Radioactivity</h3><p>Spontaneous emission from unstable nuclei. <b>Alpha:</b> Helium nucleus (2p+2n). Stopped by paper. <b>Beta:</b> Electron. Stopped by aluminum. <b>Gamma:</b> EM wave. Stopped by lead/thick concrete.</p><p><b>Half-life:</b> Time for half to decay. N = No x (1/2)^(t/t_half).</p><p><b>Applications:</b> Carbon-14 dating, medical imaging (PET scans), radiotherapy for cancer, smoke detectors, nuclear power.</p>"},
                    {"title":"Nuclear Reactions","order_index":3,"content":"<h3>Nuclear Reactions</h3><p><b>Fission:</b> Splitting heavy nucleus. Releases enormous energy. Used in nuclear plants and atom bombs.</p><p><b>Fusion:</b> Combining light nuclei. Powers the sun. Still experimental on Earth.</p><p><b>E=mc^2:</b> Small mass loss = huge energy. c^2 = 9x10^16!</p>"},
                    {"title":"Photoelectric Effect","order_index":4,"content":"<h3>Photoelectric Effect</h3><p>Light (photons) knocks electrons from metal surface. <b>Einstein equation:</b> hf = phi + KE_max.</p><p><b>Threshold frequency:</b> Minimum f to eject electron. Below threshold = no emission, regardless of intensity!</p><p><b>Applications:</b> Solar panels, light sensors, automatic doors, camera light meters.</p>"},
                    {"title":"X-rays","order_index":5,"content":"<h3>X-rays</h3><p>High-energy EM waves produced when fast electrons hit metal target. <b>Properties:</b> Penetrate soft tissue, absorbed by bone. Used for medical imaging, security scanning, crystallography.</p>"},
                    {"title":"Semiconductors and Electronics","order_index":6,"content":"<h3>Semiconductors</h3><p><b>P-type:</b> Holes (positive). <b>N-type:</b> Electrons (negative). P-N junction = diode.</p><p><b>Applications:</b> Rectifiers (AC to DC), transistors (switches/amplifiers), LEDs, solar cells, integrated circuits.</p><p><b>Logic gates:</b> AND, OR, NOT, NAND, NOR, XOR -- foundation of ALL digital electronics.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Chemistry",
        "slug": "chemistry",
        "category": "Science",
        "icon": "flask",
        "color": "#059669",
        "description": "Complete WAEC/NECO/GCE/JAMB Chemistry syllabus: Atomic structure, bonding, states of matter, kinetic theory, separation techniques, stoichiometry, acids/bases/salts, electrolysis, rates of reaction, equilibrium, energy changes, redox, organic chemistry, radioactivity, environmental chemistry",
        "lessons": [
            {
                "title": "Atomic Structure and Bonding",
                "slug": "atomic-structure-and-bonding",
                "summary": "Atomic theory, isotopes, electron configuration, periodic table, chemical bonding, shapes of molecules",
                "order_index": 1,
                "estimated_minutes": 300,
                "content": "<h2>Atomic Structure and Bonding</h2><p>Atoms are the building blocks of matter. The periodic table organizes them, and chemical bonds hold them together.</p>",
                "topics": [
                    {"title":"Atomic Structure","order_index":1,"content":"<h3>Atomic Structure</h3><p>Atoms: protons (+), neutrons (0) in nucleus; electrons (-) orbiting.</p><p><b>Atomic number (Z):</b> Number of protons (defines element). <b>Mass number (A):</b> Protons+neutrons.</p><p><b>Isotopes:</b> Same element, different neutrons. Carbon-12, Carbon-13, Carbon-14. Same chemical properties, different masses.</p><p><b>Relative atomic mass:</b> Weighted average of isotopes. Chlorine: 75% Cl-35 + 25% Cl-37 = 35.5.</p>"},
                    {"title":"Electron Configuration","order_index":2,"content":"<h3>Electron Configuration</h3><p><b>Shells:</b> K(2), L(8), M(18), N(32). Electrons fill from lowest energy.</p><p><b>Orbitals:</b> s(2), p(6), d(10), f(14). <b>Aufbau:</b> Fill 1s,2s,2p,3s,3p,4s,3d,4p...</p><p>Oxygen (8): 1s^2 2s^2 2p^4. Sodium (11): 1s^2 2s^2 2p^6 3s^1.</p>"},
                    {"title":"Periodic Table","order_index":3,"content":"<h3>Periodic Table</h3><p>Groups (columns): Same valence electrons -> similar properties. Periods (rows): Same number of shells.</p><p><b>Group 1 (Alkali metals):</b> Reactive, 1 valence electron. <b>Group 7 (Halogens):</b> Non-metals, 7 valence. <b>Group 0 (Noble gases):</b> Full outer shell, inert.</p><p><b>Trends:</b> Atomic radius increases down group (more shells) and decreases across period (more pull). Ionization energy decreases down group, increases across period.</p>"},
                    {"title":"Chemical Bonding","order_index":4,"content":"<h3>Chemical Bonding</h3><p><b>Ionic (electrovalent):</b> Electron transfer. Metal+non-metal. NaCl: Na loses e-, Cl gains e-. High melting, conduct in solution.</p><p><b>Covalent:</b> Electron sharing. Non-metal+non-metal. H2, Cl2, H2O, CH4. Low melting, don't conduct.</p><p><b>Dative (coordinate):</b> Both electrons from one atom. NH3+H+ -> NH4+.</p><p><b>Metallic:</b> Sea of delocalized electrons. Malleable, conducts electricity.</p>"},
                    {"title":"Shapes of Molecules","order_index":5,"content":"<h3>Molecular Shapes (VSEPR Theory)</h3><p>Electron pairs repel! Linear (CO2, 180), Bent (H2O, 104.5), Trigonal planar (BF3, 120), Tetrahedral (CH4, 109.5), Trigonal bipyramidal (PCl5), Octahedral (SF6).</p>"}
                ]
            },
            {
                "title": "States of Matter and Separation",
                "slug": "states-of-matter-and-separation",
                "summary": "Kinetic theory, solid, liquid, gas, changes of state, melting/boiling points, diffusion, separation techniques, mixtures",
                "order_index": 2,
                "estimated_minutes": 180,
                "content": "<h2>States of Matter</h2><p>Everything exists as solid, liquid, gas, or (rarely in WAEC) plasma. The difference is how much the particles move.</p>",
                "topics": [
                    {"title":"Kinetic Theory","order_index":1,"content":"<h3>Kinetic Theory</h3><p><b>Solid:</b> Fixed shape, particles vibrate in place. <b>Liquid:</b> Fixed volume, particles slide past. <b>Gas:</b> No fixed shape/volume, particles move freely.</p><p>As temperature increases: particles gain KE, move faster, spread apart.</p>"},
                    {"title":"Changes of State","order_index":2,"content":"<h3>Changes of State</h3><p>Melting (solid->liquid), freezing (liquid->solid), boiling/evaporation (liquid->gas), condensation (gas->liquid), sublimation (solid->gas, e.g. dry ice, iodine).</p><p><b>Melting point:</b> Temperature where solid->liquid. <b>Boiling point:</b> Temperature where liquid->gas (vapor pressure = atmospheric).</p><p><b>Evaporation vs boiling:</b> Evaporation at surface at any temp; boiling throughout at specific temp.</p>"},
                    {"title":"Diffusion","order_index":3,"content":"<h3>Diffusion</h3><p>Movement of particles from high to low concentration. <b>Graham's law:</b> Rate proportional to 1/sqrt(molar mass). Light gases diffuse faster (H2 diffuses 4x faster than O2).</p>"},
                    {"title":"Separation Techniques","order_index":4,"content":"<h3>Separation Techniques</h3><p><b>Filtration:</b> Separate solid from liquid (sand+water). <b>Crystallization:</b> Get pure solid from solution. <b>Distillation:</b> Separate liquids by boiling point (ethanol+water). <b>Fractional distillation:</b> Multiple boiling points (crude oil). <b>Chromatography:</b> Separate mixtures by solubility (inks, dyes). <b>Decantation:</b> Pour off liquid from solid.</p>"}
                ]
            },
            {
                "title": "Chemical Reactions and Equations",
                "slug": "chemical-reactions-and-equations",
                "summary": "Chemical equations, stoichiometry, mole concept, limiting reactants, percentage yield, redox reactions, balancing equations",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Chemical Reactions and Equations</h2><p>Chemical reactions rearrange atoms. Equations describe this rearrangement. The mole is the chemist's counting unit.</p>",
                "topics": [
                    {"title":"Chemical Equations","order_index":1,"content":"<h3>Chemical Equations</h3><p>Reactants -> Products. Must be BALANCED (same atoms both sides). H2 + O2 -> H2O becomes 2H2+O2 -> 2H2O.</p>"},
                    {"title":"The Mole Concept","order_index":2,"content":"<h3>The Mole</h3><p>1 mole = 6.02x10^23 particles (Avogadro's number). Moles = mass/molar mass.</p><p><b>Molar volume:</b> 1 mole of ANY gas = 22.4 L at STP.</p><p><b>Example:</b> 40g NaOH. Molar mass=40. Moles=40/40=1. Number of particles=6.02x10^23.</p><p><b>Concentration:</b> Molarity = moles/volume(L). 2M NaOH = 2 moles per liter.</p>"},
                    {"title":"Stoichiometry","order_index":3,"content":"<h3>Stoichiometry</h3><p>Use mole ratios from balanced equations. N2+3H2 -> 2NH3. Ratio N2:H2=1:3. Given 2 moles N2, need 6 moles H2, produce 4 moles NH3.</p><p><b>Limiting reactant:</b> The reactant that RUNS OUT FIRST. 2g H2 + 28g N2. Moles H2=1, N2=1. From equation, 3H2:1N2. With 1 mol N2 need 3 mol H2, but only have 1. H2 is limiting.</p>"},
                    {"title":"Redox Reactions","order_index":4,"content":"<h3>Redox</h3><p><b>Oxidation:</b> Loss of electrons, gain of oxygen. <b>Reduction:</b> Gain of electrons, loss of oxygen. OIL RIG (Oxidation Is Loss, Reduction Is Gain).</p><p><b>Oxidizing agent:</b> Causes oxidation, gets reduced. <b>Reducing agent:</b> Causes reduction, gets oxidized.</p><p><b>Oxidation numbers:</b> Track electrons. MnO4^- + 8H^+ + 5e^- -> Mn^2+ + 4H2O</p>"}
                ]
            },
            {
                "title": "Acids, Bases and Salts",
                "slug": "acids-bases-and-salts",
                "summary": "Acid-base theories, pH, indicators, reactions of acids, preparation of salts, hydrolysis, buffers",
                "order_index": 4,
                "estimated_minutes": 240,
                "content": "<h2>Acids, Bases and Salts</h2><p>Acids taste sour, bases taste bitter. But chemistry gives us a much more precise definition!</p>",
                "topics": [
                    {"title":"Acids and Bases","order_index":1,"content":"<h3>Acids and Bases</h3><p><b>Arrhenius:</b> Acid=H+ donor, Base=OH- donor. <b>Bronsted-Lowry:</b> Acid=H+ donor, Base=H+ acceptor.</p><p><b>Strong acids:</b> Fully dissociate. HCl, HNO3, H2SO4. <b>Weak acids:</b> Partially dissociate. CH3COOH, H2CO3.</p><p><b>pH scale:</b> 0-14. pH=-log[H+]. Acidic<7, neutral=7, basic>7.</p>"},
                    {"title":"Reactions of Acids","order_index":2,"content":"<h3>Acid Reactions</h3><p>Acid+Base -> Salt+Water (neutralization). <b>Acid+Metal:</b> Salt+H2. <b>Acid+Carbonate:</b> Salt+H2O+CO2.</p>"},
                    {"title":"Salts and Preparation","order_index":3,"content":"<h3>Salts</h3><p><b>Normal salt:</b> All H replaced (NaCl). <b>Acid salt:</b> Some H remaining (NaHCO3). <b>Double salt:</b> Two cations (KAl(SO4)2). <b>Complex salt:</b> Complex ion.</p><p><b>Preparation methods:</b> (1) Acid+Base. (2) Acid+Metal. (3) Acid+Carbonate. (4) Direct combination. (5) Precipitation.</p>"},
                    {"title":"Hydrolysis of Salts","order_index":4,"content":"<h3>Hydrolysis</h3><p>Salt+Water re-forms acid/base. Salt of weak acid+strong base -> alkaline solution (Na2CO3). Salt of strong acid+weak base -> acidic (NH4Cl).</p>"}
                ]
            },
            {
                "title": "Electrochemistry",
                "slug": "electrochemistry",
                "summary": "Electrolysis, faraday's laws, electrochemical cells, corrosion, applications of electrolysis",
                "order_index": 5,
                "estimated_minutes": 180,
                "content": "<h2>Electrochemistry</h2><p>Electrochemistry links chemical reactions and electricity. Electrolysis uses electricity to drive reactions. Electrochemical cells generate electricity from reactions.</p>",
                "topics": [
                    {"title":"Electrolysis","order_index":1,"content":"<h3>Electrolysis</h3><p>Using electricity to decompose a compound. <b>Cathode (-):</b> Reduction (gain electrons). <b>Anode (+):</b> Oxidation (lose electrons).</p><p><b>Electrolytes:</b> Conductive solutions (molten ionic compounds, aqueous ionic solutions). <b>Non-electrolytes:</b> Don't conduct (sugar, ethanol).</p>"},
                    {"title":"Faraday's Laws","order_index":2,"content":"<h3>Faraday's Laws</h3><p><b>First:</b> Mass deposited proportional to charge (Q=It). <b>Second:</b> Mass proportional to electrochemical equivalent.</p><p><b>m = ZIt</b> where Z = M/(nF). F=96500 C/mol, M=molar mass, n=electrons transferred.</p>"},
                    {"title":"Applications of Electrolysis","order_index":3,"content":"<h3>Applications</h3><p>(1) Electroplating (silver plating, chrome plating). (2) Extraction of metals (aluminum from Al2O3). (3) Purification of copper. (4) Production of NaOH and Cl2 from brine.</p>"},
                    {"title":"Electrochemical Cells","order_index":4,"content":"<h3>Electrochemical Cells</h3><p><b>Voltaic/galvanic cell:</b> Chemical -> Electricity (battery). <b>Daniel cell:</b> Zn|ZnSO4||CuSO4|Cu. Zn loses electrons, Cu gains.</p><p><b>Dry cell (Leclanche):</b> Common battery. Zn anode, carbon cathode, MnO2 paste.</p><p><b>Lead-acid battery:</b> Car battery. Pb|H2SO4|PbO2. Rechargeable.</p>"}
                ]
            },
            {
                "title": "Rate of Reaction and Equilibrium",
                "slug": "rate-of-reaction-and-equilibrium",
                "summary": "Factors affecting rate, collision theory, activation energy, catalysts, reversible reactions, Le Chatelier's principle",
                "order_index": 6,
                "estimated_minutes": 180,
                "content": "<h2>Rate of Reaction and Equilibrium</h2><p>Some reactions happen in a flash (explosion), others take years (rusting). Why?</p>",
                "topics": [
                    {"title":"Rate of Reaction","order_index":1,"content":"<h3>Rate of Reaction</h3><p><b>Factors:</b> Concentration, temperature, surface area, catalyst, pressure (gases).</p><p><b>Collision theory:</b> Particles must collide with correct orientation AND sufficient energy (>= activation energy).</p><p><b>Temperature:</b> Every 10C roughly DOUBLES rate (more particles have enough energy).</p>"},
                    {"title":"Catalysis","order_index":2,"content":"<h3>Catalysis</h3><p>Speeds up reaction WITHOUT being consumed. Lowers activation energy by providing alternative pathway.</p><p><b>Examples:</b> Fe in Haber process (NH3), V2O5 in Contact process (H2SO4), Pt in catalytic converters, enzymes in body.</p>"},
                    {"title":"Chemical Equilibrium","order_index":3,"content":"<h3>Equilibrium</h3><p>Reversible reactions reach dynamic equilibrium (forward rate = backward rate).</p><p><b>Le Chatelier:</b> If you change conditions, system shifts to OPPOSE the change.</p><p><b>Temperature up:</b> Shifts toward endothermic direction. <b>Pressure up:</b> Shifts toward fewer gas molecules. <b>Concentration up:</b> Shifts away from added substance.</p><p><b>N2+3H2 ? 2NH3, ?H=-ve.</b> Industrial: 200-500atm, 450C, Fe catalyst. Low temp favors yield but too slow. Compromise!</p>"}
                ]
            },
            {
                "title": "Organic Chemistry",
                "slug": "organic-chemistry",
                "summary": "Hydrocarbons, alkanes, alkenes, alkynes, functional groups, alcohols, carboxylic acids, polymers, petroleum, fractional distillation",
                "order_index": 7,
                "estimated_minutes": 360,
                "content": "<h2>Organic Chemistry</h2><p>Carbon is special! It forms 4 bonds and makes millions of compounds -- from methane to DNA. Organic chemistry is the chemistry of life.</p>",
                "topics": [
                    {"title":"Alkanes","order_index":1,"content":"<h3>Alkanes (Saturated Hydrocarbons)</h3><p>CnH2n+2. Single bonds only. <b>First 10:</b> Methane(CH4), Ethane(C2H6), Propane(C3H8), Butane(C4H10), Pentane(C5H12), Hexane(C6H14), Heptane(C7H16), Octane(C8H18), Nonane(C9H20), Decane(C10H22).</p><p><b>Properties:</b> Relatively unreactive. Burn cleanly (CO2+H2O). Used as fuels.</p><p><b>Substitution reactions:</b> With halogens in UV light. CH4+Cl2 -> CH3Cl+HCl (chloromethane).</p><p><b>Isomerism:</b> Butane: normal (straight chain) and isobutane (branched). Different structures, same formula.</p>"},
                    {"title":"Alkenes","order_index":2,"content":"<h3>Alkenes (Unsaturated)</h3><p>CnH2n. Contain C=C double bond. <b>First:</b> Ethene(C2H4), Propene(C3H6).</p><p><b>Addition reactions:</b> Double bond opens. Ethene+H2O -> Ethanol (steam cracking).</p><p><b>Test for unsaturation:</b> Decolorizes bromine water (orange to colorless). Make sure to know this!</p>"},
                    {"title":"Alkynes","order_index":3,"content":"<h3>Alkynes (Triple Bond)</h3><p>CnH2n-2. <b>C2H2:</b> Ethyne (acetylene) -- used in welding torches (very hot flame!).</p>"},
                    {"title":"Functional Groups","order_index":4,"content":"<h3>Functional Groups</h3><p><b>Alcohols (R-OH):</b> Ethanol (CH3CH2OH) -- fermentation, alcoholic drinks, fuel.</p><p><b>Aldehydes (R-CHO):</b> Methanal (formaldehyde), Ethanal (acetaldehyde).</p><p><b>Ketones (R-CO-R'):</b> Propanone (acetone) -- nail polish remover.</p><p><b>Carboxylic acids (R-COOH):</b> Methanoic (formic), Ethanoic (acetic/vinegar). Weak acids.</p><p><b>Esters (R-COO-R'):</b> Fruity smells! Used in perfumes, flavorings.</p><p><b>Amines (R-NH2):</b> Amino acids -> proteins.</p>"},
                    {"title":"Polymers","order_index":5,"content":"<h3>Polymers</h3><p>Long chains of repeating units (monomers). <b>Addition polymerization:</b> Ethene -> Poly(ethene). <b>Condensation:</b> Nylon, polyester.</p><p><b>Natural polymers:</b> Proteins (amino acids), carbohydrates (glucose->starch/cellulose), rubber (isoprene), DNA.</p><p><b>Synthetic:</b> Nylon (stockings, ropes), Polythene (bags), PVC (pipes), Polystyrene (foam), Teflon (non-stick).</p>"},
                    {"title":"Petroleum and Fractional Distillation","order_index":6,"content":"<h3>Petroleum</h3><p>Crude oil is a mixture of hydrocarbons. <b>Fractional distillation:</b> Separate by boiling point (tall tower).</p><p><b>Fractions (from top to bottom):</b> Refinery gas (C1-4, bottled gas), Gasoline/Petrol (C5-10, car fuel), Kerosene (C11-13, jet fuel), Diesel (C14-20, trucks), Fuel oil (C20-30, ships), Bitumen (C30+, roads).</p><p><b>Cracking:</b> Breaking long chains. Thermal (high temp) or catalytic (zeolite catalyst). Produces more petrol and alkenes.</p>"}
                ]
            },
            {
                "title": "Energy Changes and Thermochemistry",
                "slug": "energy-changes-and-thermochemistry",
                "summary": "Exothermic vs endothermic, enthalpy, bond energy, Hess's law, calorimetry",
                "order_index": 8,
                "estimated_minutes": 120,
                "content": "<h2>Energy Changes</h2><p>Every chemical reaction either RELEASES or ABSORBS energy as heat.</p>",
                "topics": [
                    {"title":"Exothermic and Endothermic","order_index":1,"content":"<h3>Exothermic and Endothermic</h3><p><b>Exothermic:</b> Releases heat (?H negative). Surroundings get hotter. Combustion, neutralization, respiration.</p><p><b>Endothermic:</b> Absorbs heat (?H positive). Surroundings get colder. Photosynthesis, dissolving NH4NO3.</p><p><b>Bond energy:</b> Energy to break bond. Breaking=endothermic, making=exothermic. ?H = bonds broken - bonds made.</p>"}
                ]
            },
            {
                "title": "Water and Solutions",
                "slug": "water-and-solutions",
                "summary": "Water as solvent, hardness, solubility, solubility curves, crystallization",
                "order_index": 9,
                "estimated_minutes": 120,
                "content": "<h2>Water and Solutions</h2><p>Water is the universal solvent. Its unique properties make life possible.</p>",
                "topics": [
                    {"title":"Water","order_index":1,"content":"<h3>Water</h3><p><b>Hard water:</b> Contains Ca2+/Mg2+ ions. Temporary (bicarbonates, removed by boiling). Permanent (sulfates/chlorides, removed by ion exchange).</p><p>Disadvantages: Wastes soap, forms scale in kettles/pipes. Advantages: Better taste, provides Ca2+ for teeth/bones.</p>"},
                    {"title":"Solubility","order_index":2,"content":"<h3>Solubility</h3><p>Maximum solute that dissolves at given temp. <b>Solubility curves:</b> Most solids more soluble at higher temp. Gases LESS soluble at higher temp (fizzy drinks go flat when warm).</p>"}
                ]
            },
            {
                "title": "Environmental and Industrial Chemistry",
                "slug": "environmental-and-industrial-chemistry",
                "summary": "Air pollution, water pollution, greenhouse effect, ozone layer, industrial processes, extraction of metals",
                "order_index": 10,
                "estimated_minutes": 180,
                "content": "<h2>Environmental Chemistry</h2><p>Chemistry explains both the causes and solutions of environmental problems.</p>",
                "topics": [
                    {"title":"Air Pollution","order_index":1,"content":"<h3>Air Pollution</h3><p><b>CO:</b> Incomplete combustion, poisonous. <b>SO2:</b> Burning coal/oil, causes acid rain. <b>NOx:</b> Car engines, acid rain + smog. <b>CFCs:</b> Destroy ozone layer (banned by Montreal Protocol).</p><p><b>Greenhouse gases:</b> CO2, CH4, H2O vapor. Trap heat -- necessary for life, but too much = global warming.</p><p><b>Catalytic converter:</b> 2CO+2NO -> 2CO2+N2. Converts toxic gases to harmless.</p>"},
                    {"title":"Industrial Chemistry","order_index":2,"content":"<h3>Industrial Processes</h3><p><b>Haber process:</b> N2+3H2 -> 2NH3 (fertilizer). <b>Contact process:</b> S->SO2->SO3->H2SO4. <b>Solvay process:</b> Na2CO3 from NaCl+CaCO3.</p><p><b>Extraction of metals:</b> Electrolysis for reactive (Al, Na), reduction with C for less reactive (Fe, Zn), native for unreactive (Au, Ag).</p>"}
                ]
            },
            {
                "title": "Radioactivity and Nuclear Chemistry",
                "slug": "radioactivity-and-nuclear-chemistry",
                "summary": "Types of radiation, half-life, nuclear equations, applications of radioactivity, nuclear fission and fusion",
                "order_index": 11,
                "estimated_minutes": 120,
                "content": "<h2>Radioactivity and Nuclear Chemistry</h2><p>Some nuclei are unstable and spontaneously emit radiation. The energy involved is millions of times greater than chemical reactions.</p>",
                "topics": [
                    {"title":"Radioactivity","order_index":1,"content":"<h3>Radioactivity</h3><p><b>Alpha (a):</b> 2p+2n, He nucleus. Low penetration (stopped by paper). Highly ionizing.</p><p><b>Beta (b):</b> Electron from nucleus (neutron to proton + e-). Moderate penetration (stopped by aluminum).</p><p><b>Gamma (g):</b> EM wave, no mass. High penetration (stopped by lead/concrete). Low ionization.</p><p><b>Half-life:</b> Time for half to decay. C-14: 5730 years. Used for carbon dating.</p><p><b>Nuclear equations:</b> Uranium-238 decays: U-238 to Th-234 + a.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Biology",
        "slug": "biology",
        "category": "Science",
        "icon": "leaf",
        "color": "#16A34A",
        "description": "Complete WAEC/NECO/GCE/JAMB Biology syllabus: Cell biology, genetics, evolution, ecology, physiology, reproduction, classification, plant and animal biology -- all with real-world examples and exam-focused explanations",
        "lessons": [
            {
                "title": "Cell Biology",
                "slug": "cell-biology",
                "summary": "Cell theory, cell structure, organelles, cell division, transport across membranes, enzymes, cellular respiration, photosynthesis",
                "order_index": 1,
                "estimated_minutes": 360,
                "content": "<h2>Cell Biology</h2><p>The cell is the basic unit of life. Every living thing is made of cells. Understanding cells is the foundation of ALL biology.</p>",
                "topics": [
                    {"title":"Cell Theory and Cell Structure","order_index":1,"content":"<h3>Cell Theory</h3><p>(1) All living things are made of cells. (2) The cell is the basic unit of life. (3) All cells come from pre-existing cells.</p><p><b>Animal cell:</b> Cell membrane, cytoplasm, nucleus, mitochondria, ribosomes, ER, Golgi, lysosomes.</p><p><b>Plant cell:</b> All of the above + cell wall (cellulose), chloroplasts, large central vacuole, plasmodesmata.</p><p><b>Differences:</b> Plants have cell wall, chloroplasts, large vacuole. Animals don't.</p>"},
                    {"title":"Organelles and Their Functions","order_index":2,"content":"<h3>Organelle Functions</h3><p><b>Nucleus:</b> Contains DNA, controls cell. <b>Mitochondria:</b> Powerhouse, makes ATP (cellular respiration). <b>Ribosomes:</b> Protein synthesis. <b>Rough ER:</b> Protein processing. <b>Smooth ER:</b> Lipid synthesis.</p><p><b>Golgi apparatus:</b> Packaging and shipping. <b>Lysosomes:</b> Digestion and waste disposal. <b>Chloroplasts:</b> Photosynthesis. <b>Vacuole:</b> Storage and support.</p>"},
                    {"title":"Cell Division (Mitosis and Meiosis)","order_index":3,"content":"<h3>Mitosis and Meiosis</h3><p><b>Mitosis:</b> 1 division -> 2 identical diploid daughter cells. Growth and repair. Prophase, Metaphase, Anaphase, Telophase (PMAT).</p><p><b>Meiosis:</b> 2 divisions -> 4 genetically different haploid cells. Gametes (sperm/egg). Crossing over = genetic variation.</p><p><b>Difference:</b> Mitosis = 2 identical cells; Meiosis = 4 different cells with half chromosomes.</p>"},
                    {"title":"Transport Across Cell Membrane","order_index":4,"content":"<h3>Transport</h3><p><b>Diffusion:</b> High to low concentration, no energy. O2, CO2.</p><p><b>Osmosis:</b> Water across semi-permeable membrane from dilute to concentrated.</p><p><b>Active transport:</b> Low to high concentration, NEEDS energy (ATP). Protein pumps. Example: root hair cells absorbing mineral ions.</p>"},
                    {"title":"Enzymes","order_index":5,"content":"<h3>Enzymes</h3><p>Biological catalysts (mostly proteins). <b>Lock and key:</b> Specific shape fits specific substrate.</p><p><b>Factors:</b> Temperature (denatures above ~40C), pH (each enzyme has optimal, e.g. pepsin pH2, trypsin pH8), concentration.</p><p><b>Examples:</b> Amylase (starch->maltose), Pepsin (protein->peptides), Catalase (H2O2->H2O+O2).</p>"},
                    {"title":"Cellular Respiration","order_index":6,"content":"<h3>Cellular Respiration</h3><p><b>Aerobic:</b> Glucose+O2 -> CO2+H2O+ATP. C6H12O6+6O2 -> 6CO2+6H2O+38 ATP (mitochondria).</p><p><b>Anaerobic:</b> No O2. Plants/yeast: Glucose -> Ethanol+CO2+2 ATP. Animals: Glucose -> Lactic acid+2 ATP (muscle burn!).</p>"},
                    {"title":"Photosynthesis","order_index":7,"content":"<h3>Photosynthesis</h3><p>6CO2+6H2O+light -> C6H12O6+6O2. Happens in CHLOROPLASTS (chlorophyll pigment).</p><p><b>Light stage:</b> Light splits water (photolysis). Makes ATP and reduced NADP. <b>Dark stage (Calvin cycle):</b> CO2 fixed into glucose using ATP and NADPH.</p><p><b>Limiting factors:</b> Light intensity, CO2 concentration, temperature.</p>"}
                ]
            },
            {
                "title": "Genetics and Evolution",
                "slug": "genetics-and-evolution",
                "summary": "DNA structure, genes, chromosomes, inheritance, Mendel's laws, monohybrid/dihybrid crosses, sex determination, variation, evolution, natural selection",
                "order_index": 2,
                "estimated_minutes": 300,
                "content": "<h2>Genetics and Evolution</h2><p>Why do children look like their parents? How do species change over time? Genetics and evolution answer these questions.</p>",
                "topics": [
                    {"title":"DNA and Chromosomes","order_index":1,"content":"<h3>DNA</h3><p>Double helix (Watson & Crick, 1953). <b>Nucleotides:</b> Sugar(deoxyribose)+Phosphate+Base. <b>Bases:</b> A pairs with T, C pairs with G.</p><p><b>Gene:</b> Section of DNA coding for a protein. <b>Chromosome:</b> Long DNA molecule + proteins. Humans: 23 pairs (46 total).</p><p><b>DNA replication:</b> Unzip, each strand acts as template for new strand. 'Semi-conservative'.</p>"},
                    {"title":"Mendelian Inheritance","order_index":2,"content":"<h3>Mendel's Laws</h3><p><b>Law of Segregation:</b> Alleles separate during gamete formation. <b>Law of Independent Assortment:</b> Different genes sort independently.</p><p><b>Dominant (A):</b> Expressed if present. <b>Recessive (a):</b> Only expressed if both recessive. <b>Genotype:</b> Genetic makeup (AA, Aa, aa). <b>Phenotype:</b> Physical appearance.</p>"},
                    {"title":"Monohybrid Cross","order_index":3,"content":"<h3>Monohybrid Cross</h3><p>One trait. Example: Tall (T) dominant over short (t). Tt x Tt -> 3:1 ratio tall:short. Genotype: 1TT:2Tt:1tt.</p><p><b>Test cross:</b> Unknown dominant (T?) x recessive (tt). If any short offspring = parent was Tt.</p>"},
                    {"title":"Dihybrid Cross","order_index":4,"content":"<h3>Dihybrid Cross</h3><p>Two traits. Round+yellow (RRYY) x wrinkled+green (rryy). F1 all RrYy. F2: 9:3:3:1 ratio.</p>"},
                    {"title":"Sex Determination","order_index":5,"content":"<h3>Sex Determination</h3><p>Females: XX. Males: XY. Mother always gives X. Father gives X (girl) or Y (boy). 50% probability each.</p><p><b>Sex-linked traits:</b> Genes on X chromosome. Color blindness, hemophilia. Males more affected (only one X).</p>"},
                    {"title":"Variation and Evolution","order_index":6,"content":"<h3>Evolution</h3><p><b>Natural selection (Darwin):</b> (1) Variation exists. (2) More offspring than can survive. (3) Struggle for existence. (4) Fittest survive and reproduce. (5) Over generations, population changes.</p><p><b>Evidence:</b> Fossils, comparative anatomy (homologous structures), embryology, DNA similarity, antibiotic resistance in bacteria.</p><p><b>Mutation:</b> Random change in DNA. Most harmful, some neutral, few beneficial. Source of all new variation.</p>"}
                ]
            },
            {
                "title": "Ecology",
                "slug": "ecology",
                "summary": "Ecosystems, food chains/webs, nutrient cycles, population dynamics, biomes, pollution, conservation, adaptation",
                "order_index": 3,
                "estimated_minutes": 240,
                "content": "<h2>Ecology</h2><p>Ecology studies how organisms interact with each other and their environment. It tells us how ecosystems work and why we must protect them.</p>",
                "topics": [
                    {"title":"Ecosystems and Food Chains","order_index":1,"content":"<h3>Ecosystems</h3><p>Community of organisms + their environment. <b>Producers:</b> Plants (photosynthesis). <b>Consumers:</b> Primary (herbivores), Secondary (carnivores), Tertiary (top carnivores). <b>Decomposers:</b> Bacteria and fungi.</p><p><b>Food chain:</b> Grass -> Grasshopper -> Frog -> Snake -> Hawk. Each arrow = energy transfer. Only 10% passes to next level!</p>"},
                    {"title":"Nutrient Cycles","order_index":2,"content":"<h3>Cycles</h3><p><b>Carbon cycle:</b> Photosynthesis (CO2->glucose), Respiration (glucose->CO2), Combustion, Decomposition. CO2 released by burning fossil fuels -> global warming.</p><p><b>Nitrogen cycle:</b> N2 in air -> Nitrogen fixation (bacteria/lightning) -> Nitrates -> Plants -> Animals -> Decomposition -> Ammonia -> Nitrification (Nitrosomonas->NO2-, Nitrobacter->NO3-) -> Denitrification (back to N2).</p>"},
                    {"title":"Population and Biomes","order_index":3,"content":"<h3>Population Ecology</h3><p><b>Factors affecting:</b> Birth rate, death rate, immigration, emigration. <b>Carrying capacity:</b> Maximum population environment can support. <b>Competition:</b> Within species (intraspecific) and between species (interspecific).</p><p><b>Biomes:</b> Tropical rainforest (hot, wet), Savanna (grassland+trees), Desert (very dry), Temperate forest (4 seasons), Tundra (cold, permafrost), Taiga (coniferous forest).</p>"},
                    {"title":"Pollution and Conservation","order_index":4,"content":"<h3>Pollution</h3><p><b>Air:</b> CO2 (global warming), SO2/NOx (acid rain), CFCs (ozone hole). <b>Water:</b> Eutrophication (fertilizers->algae bloom->death of aquatic life). <b>Land:</b> Plastics (non-biodegradable), toxic waste.</p><p><b>Conservation:</b> National parks, reforestation, sustainable fishing, recycling, renewable energy, endangered species protection.</p>"}
                ]
            },
            {
                "title": "Physiology",
                "slug": "physiology",
                "summary": "Digestive system, respiratory system, circulatory system, excretory system, nervous system, endocrine system, reproductive system",
                "order_index": 4,
                "estimated_minutes": 360,
                "content": "<h2>Physiology</h2><p>Your body is a collection of organ systems working together. Each system has a job, and all must cooperate for health.</p>",
                "topics": [
                    {"title":"Digestive System","order_index":1,"content":"<h3>Digestion</h3><p><b>Path:</b> Mouth (chewing, amylase) -> Esophagus (peristalsis) -> Stomach (HCl, pepsin) -> Small intestine (bile from liver, enzymes from pancreas, absorption through villi) -> Large intestine (water absorption) -> Rectum/Anus.</p><p><b>Enzymes:</b> Amylase (starch->maltose), Pepsin (protein->peptides), Trypsin (peptides->amino acids), Lipase (fats->fatty acids+glycerol).</p>"},
                    {"title":"Respiratory System","order_index":2,"content":"<h3>Respiration</h3><p><b>Path:</b> Nose/Mouth -> Trachea -> Bronchi -> Bronchioles -> Alveoli (gas exchange).</p><p><b>Inhale:</b> Diaphragm contracts (down), rib cage up, volume up, pressure down, air in. <b>Exhale:</b> Opposite.</p><p><b>Gas exchange:</b> Alveoli have thin walls + rich blood supply. O2 diffuses into blood. CO2 diffuses out.</p>"},
                    {"title":"Circulatory System","order_index":3,"content":"<h3>Circulation</h3><p><b>Heart:</b> 4 chambers. Right side = deoxygenated blood to lungs. Left side = oxygenated to body.</p><p><b>Blood vessels:</b> Arteries (thick, high pressure, away from heart), Veins (thin, valves, to heart), Capillaries (one-cell thick, gas/nutrient exchange).</p><p><b>Blood components:</b> Red blood cells (O2 transport, hemoglobin), White blood cells (immunity), Platelets (clotting), Plasma (carries nutrients/hormones/waste).</p>"},
                    {"title":"Excretory System","order_index":4,"content":"<h3>Excretion</h3><p><b>Kidneys:</b> Filter blood. Nephron = functional unit. Filtration (glomerulus), Reabsorption (useful substances back), Secretion (waste in).</p><p><b>Skin:</b> Sweat glands excrete water+salts+urea. Also cools body through evaporation.</p><p><b>Lungs:</b> Excrete CO2. <b>Liver:</b> Breaks down toxins, produces urea from ammonia.</p>"},
                    {"title":"Nervous System","order_index":5,"content":"<h3>Nervous System</h3><p><b>Central (CNS):</b> Brain + Spinal cord. <b>Peripheral (PNS):</b> Nerves connecting CNS to body.</p><p><b>Neuron:</b> Cell body, dendrites (receive), axon (send). <b>Synapse:</b> Gap between neurons. Chemical (neurotransmitter) or electrical signal.</p><p><b>Reflex arc:</b> Stimulus -> Receptor -> Sensory neuron -> Relay neuron (spinal cord) -> Motor neuron -> Effector (muscle). No brain involvement!</p>"},
                    {"title":"Endocrine System","order_index":6,"content":"<h3>Hormones</h3><p>Chemical messengers via bloodstream. <b>Pituitary:</b> Master gland (GH, TSH, FSH, LH). <b>Thyroid:</b> Thyroxine (metabolism). <b>Pancreas:</b> Insulin (lowers blood sugar), Glucagon (raises). <b>Adrenal:</b> Adrenaline (fight/flight). <b>Ovaries:</b> Estrogen, Progesterone. <b>Testes:</b> Testosterone.</p>"},
                    {"title":"Reproductive System","order_index":7,"content":"<h3>Reproduction</h3><p><b>Male:</b> Testes (sperm production), Epididymis (storage), Vas deferens, Seminal vesicles, Prostate, Urethra, Penis.</p><p><b>Female:</b> Ovaries (egg production), Fallopian tubes (fertilization site), Uterus (implantation, pregnancy), Cervix, Vagina.</p><p><b>Menstrual cycle:</b> FSH -> follicle matures -> estrogen -> LH -> ovulation (day 14) -> progesterone -> prepare uterus. No pregnancy = menstruation.</p>"}
                ]
            },
            {
                "title": "Classification and Diversity",
                "slug": "classification-and-diversity",
                "summary": "Five kingdoms, binomial nomenclature, viruses, bacteria, protists, fungi, plants, animals, invertebrates and vertebrates",
                "order_index": 5,
                "estimated_minutes": 240,
                "content": "<h2>Classification and Diversity</h2><p>There are millions of species. Classification helps us organize and understand this diversity.</p>",
                "topics": [
                    {"title":"Classification","order_index":1,"content":"<h3>Classification Hierarchy</h3><p>Domain -> Kingdom -> Phylum -> Class -> Order -> Family -> Genus -> Species. Mnemonic: King Philip Came Over For Good Soup.</p><p><b>Five Kingdoms:</b> Monera (bacteria), Protista (amoeba, paramecium), Fungi (mushrooms, yeast), Plantae (plants), Animalia (animals).</p>"},
                    {"title":"Kingdom Monera and Protista","order_index":2,"content":"<h3>Bacteria and Protists</h3><p><b>Bacteria:</b> Prokaryotes (no nucleus). Binary fission. Cocci (sphere), Bacilli (rod), Spirilla (spiral). Heterotrophic or autotrophic. Useful: decomposition, nitrogen fixation, yogurt. Harmful: TB, cholera, typhoid.</p><p><b>Protists:</b> Eukaryotes, mostly single-celled. Amoeba (pseudopodia), Paramecium (cilia), Euglena (flagellum, has chloroplasts!).</p>"},
                    {"title":"Kingdom Fungi","order_index":3,"content":"<h3>Fungi</h3><p>Eukaryotes, heterotrophic (absorption). Cell wall of chitin. <b>Examples:</b> Mushroom (basidiomycete), Yeast (single-celled, budding), Rhizopus (bread mold).</p><p><b>Useful:</b> Baking/brewing (yeast), antibiotics (Penicillium), decomposition. <b>Harmful:</b> Athlete's foot, ringworm, crop diseases.</p>"},
                    {"title":"Kingdom Plantae","order_index":4,"content":"<h3>Plants</h3><p><b>Non-vascular:</b> Mosses (Bryophytes). No true roots/stems. <b>Vascular:</b> Ferns (Pteridophytes), Gymnosperms (conifers, naked seeds), Angiosperms (flowering plants).</p><p><b>Angiosperms:</b> Monocots (one cotyledon, parallel veins, fibrous roots) vs Dicots (two cotyledons, network veins, tap root).</p>"},
                    {"title":"Kingdom Animalia","order_index":5,"content":"<h3>Animal Phyla</h3><p><b>Invertebrates:</b> Porifera (sponges), Cnidaria (jellyfish), Platyhelminthes (flatworms), Nematoda (roundworms), Annelida (segmented worms), Mollusca (snails), Arthropoda (insects, crustaceans, arachnids), Echinodermata (starfish).</p><p><b>Vertebrates:</b> Fish (gills, scales), Amphibians (moist skin, metamorphosis), Reptiles (scales, eggs on land), Birds (feathers, warm-blooded), Mammals (hair, milk mammary glands).</p>"}
                ]
            }
        ]
    },
    {
        "name": "Economics",
        "slug": "economics",
        "category": "Social Sciences",
        "icon": "trending-up",
        "color": "#D97706",
        "description": "Complete WAEC/NECO/GCE/JAMB Economics syllabus: Microeconomics, macroeconomics, national income, money and banking, public finance, international trade, economic development -- all with Nigerian/West African context",
        "lessons": [
            {
                "title": "Fundamentals of Economics",
                "slug": "fundamentals-of-economics",
                "summary": "Scarcity, opportunity cost, production possibility curve, economic systems, basic economic problems",
                "order_index": 1,
                "estimated_minutes": 180,
                "content": "<h2>Fundamentals of Economics</h2><p>Economics studies how we make choices with LIMITED resources but UNLIMITED wants. It's the science of scarcity.</p>",
                "topics": [
                    {"title":"Basic Concepts","order_index":1,"content":"<h3>Basic Concepts</h3><p><b>Scarcity:</b> Resources are limited relative to wants. The fundamental economic problem.</p><p><b>Opportunity cost:</b> The NEXT BEST alternative forgone. If you buy a N5000 shirt, the opportunity cost might be the N5000 textbook you didn't buy.</p><p><b>Three basic questions:</b> WHAT to produce? HOW to produce? FOR WHOM to produce?</p>"},
                    {"title":"Production Possibility Curve","order_index":2,"content":"<h3>PPC</h3><p>Shows maximum combinations of two goods. Points ON curve = efficient. INSIDE = inefficient. OUTSIDE = unattainable (currently).</p><p>Economic growth = curve shifts OUTWARD (more resources or better technology).</p>"},
                    {"title":"Economic Systems","order_index":3,"content":"<h3>Economic Systems</h3><p><b>Capitalism (free market):</b> Private ownership, price mechanism, profit motive. USA, UK.</p><p><b>Socialism (command):</b> State ownership, central planning. Cuba, North Korea.</p><p><b>Mixed economy:</b> Both private and public sectors. Nigeria, most countries.</p>"}
                ]
            },
            {
                "title": "Microeconomics",
                "slug": "microeconomics",
                "summary": "Demand and supply, elasticity, utility theory, production, costs, revenue, market structures, price determination",
                "order_index": 2,
                "estimated_minutes": 360,
                "content": "<h2>Microeconomics</h2><p>Micro looks at individual decisions: consumers, firms, markets. How are prices determined? How do firms decide output?</p>",
                "topics": [
                    {"title":"Demand","order_index":1,"content":"<h3>Demand</h3><p>Quantity consumers WILLING and ABLE to buy at various prices. <b>Law:</b> Price up -> demand down (ceteris paribus).</p><p><b>Movement along:</b> Price change. <b>Shift:</b> Income, preferences, population, prices of related goods (substitutes/complements), expectations.</p>"},
                    {"title":"Supply","order_index":2,"content":"<h3>Supply</h3><p>Quantity producers are WILLING and ABLE to sell. <b>Law:</b> Price up -> supply up.</p><p><b>Shift factors:</b> Technology, input costs, taxes, subsidies, number of sellers, expectations.</p>"},
                    {"title":"Equilibrium Price","order_index":3,"content":"<h3>Equilibrium</h3><p>Where quantity demanded = quantity supplied. No shortage, no surplus.</p><p><b>Price above equilibrium:</b> Surplus (excess supply). <b>Price below:</b> Shortage (excess demand).</p>"},
                    {"title":"Elasticity","order_index":4,"content":"<h3>Elasticity</h3><p><b>PED = %change in Qd / %change in P.</b> Elastic >1, Inelastic <1, Unit =1.</p><p><b>Determinants of PED:</b> Necessity vs luxury, availability of substitutes, time period, proportion of income.</p><p><b>Total revenue and PED:</b> Inelastic -> price up = total revenue up. Elastic -> price up = total revenue down.</p>"},
                    {"title":"Utility Theory","order_index":5,"content":"<h3>Utility</h3><p>Satisfaction from consumption. <b>Total utility:</b> Total satisfaction. <b>Marginal utility:</b> Extra satisfaction from one more unit. Diminishing marginal utility: each extra unit gives less satisfaction.</p>"},
                    {"title":"Production and Costs","order_index":6,"content":"<h3>Production</h3><p><b>Short run:</b> At least one factor fixed. <b>Long run:</b> All factors variable. <b>Law of diminishing returns:</b> Adding more variable factor to fixed factor eventually gives less extra output.</p><p><b>Costs:</b> FC (fixed, rent), VC (variable, wages), TC = FC+VC. MC = change in TC/change in output. AC = TC/Q.</p>"},
                    {"title":"Market Structures","order_index":7,"content":"<h3>Market Structures</h3><p><b>Perfect competition:</b> Many firms, identical products, price takers, free entry.</p><p><b>Monopoly:</b> One firm, unique product, price maker, barriers to entry.</p><p><b>Monopolistic competition:</b> Many firms, differentiated products (restaurants, salons).</p><p><b>Oligopoly:</b> Few large firms, interdependence (banks, telecoms).</p>"}
                ]
            },
            {
                "title": "Macroeconomics",
                "slug": "macroeconomics",
                "summary": "National income, employment, inflation, fiscal policy, monetary policy, economic growth",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Macroeconomics</h2><p>Macro looks at the WHOLE economy. GDP, inflation, unemployment, economic growth -- the big picture.</p>",
                "topics": [
                    {"title":"National Income","order_index":1,"content":"<h3>National Income</h3><p><b>GDP:</b> Total value of goods/services in a country. <b>GNP:</b> GDP + net income from abroad.</p><p><b>Measurements:</b> Output, Income, Expenditure (all should give same total!). Y=C+I+G+(X-M).</p>"},
                    {"title":"Inflation","order_index":2,"content":"<h3>Inflation</h3><p>General rise in prices. <b>Demand-pull:</b> Too much money chasing too few goods. <b>Cost-push:</b> Rising costs of production.</p><p><b>Effects:</b> Fixed income suffers, savers lose, borrowers gain, uncertainty for business.</p>"},
                    {"title":"Unemployment","order_index":3,"content":"<h3>Unemployment</h3><p><b>Types:</b> Frictional (between jobs), Structural (skills mismatch), Cyclical (recession), Seasonal (farming, tourism).</p>"},
                    {"title":"Money and Banking","order_index":4,"content":"<h3>Money and Banking</h3><p><b>Functions of money:</b> Medium of exchange, store of value, unit of account, standard of deferred payment.</p><p><b>Central bank (CBN):</b> Controls money supply, regulates banks, sets interest rate (MPR), prints currency, lender of last resort.</p><p><b>Commercial banks:</b> Accept deposits, give loans, create credit (fractional reserve system).</p>"},
                    {"title":"Fiscal Policy","order_index":5,"content":"<h3>Fiscal Policy</h3><p>Government spending + Taxation (budget). <b>Expansionary:</b> Increase spending, cut taxes -> stimulate economy (in recession). <b>Contractionary:</b> Decrease spending, raise taxes -> cool economy (reduce inflation).</p>"},
                    {"title":"Monetary Policy","order_index":6,"content":"<h3>Monetary Policy</h3><p>CBN tools: Interest rate (MPR), Cash reserve ratio (CRR), Open market operations (OMO), Moral suasion.</p><p><b>Expansionary:</b> Lower rates, buy bonds -> increase money supply. <b>Contractionary:</b> Raise rates, sell bonds -> decrease money supply.</p>"}
                ]
            },
            {
                "title": "Public Finance and International Trade",
                "slug": "public-finance-and-international-trade",
                "summary": "Government revenue, taxation, budget, balance of payments, exchange rates, WTO, ECOWAS, terms of trade",
                "order_index": 4,
                "estimated_minutes": 240,
                "content": "<h2>Public Finance and International Trade</h2><p>How government raises and spends money. How countries trade with each other.</p>",
                "topics": [
                    {"title":"Public Finance","order_index":1,"content":"<h3>Government Revenue and Expenditure</h3><p><b>Revenue sources:</b> Taxes (direct and indirect), oil, fees, grants, loans.</p><p><b>Taxation principles (canons):</b> Equity, certainty, convenience, economy, flexibility.</p><p><b>Direct tax:</b> Paid directly by person (income tax, company tax). <b>Indirect tax:</b> Paid through consumption (VAT, customs duties).</p><p><b>Progressive:</b> Higher rate for higher income. <b>Regressive:</b> Lower % for higher income. <b>Proportional:</b> Same % for all.</p>"},
                    {"title":"International Trade","order_index":2,"content":"<h3>International Trade</h3><p>Countries trade because of comparative advantage (can produce at lower opportunity cost).</p><p><b>Balance of payments:</b> Records ALL transactions between a country and the rest of the world. Current account (goods, services, income) + Capital account.</p><p><b>Exchange rates:</b> Fixed (government sets), Floating (market sets), Managed float.</p><p><b>Protectionism:</b> Tariffs (tax on imports), Quotas (limits), Embargoes (ban). Purpose: protect domestic industries, reduce trade deficit.</p>"}
                ]
            },
            {
                "title": "Economic Development",
                "slug": "economic-development",
                "summary": "Economic growth vs development, developing countries, agriculture, industrialization, population, poverty, international economic organizations",
                "order_index": 5,
                "estimated_minutes": 180,
                "content": "<h2>Economic Development</h2><p>Growth is about MORE output. Development is about BETTER lives.</p>",
                "topics": [
                    {"title":"Development","order_index":1,"content":"<h3>Economic Development</h3><p><b>Indicators:</b> GDP per capita, literacy rate, life expectancy, HDI (Human Development Index), poverty rate, access to clean water/healthcare.</p><p><b>Obstacles to development:</b> Capital shortage, low savings, corruption, poor infrastructure, debt burden, unfavorable terms of trade.</p><p><b>Strategies:</b> Import substitution, export promotion, foreign aid, microfinance, entrepreneurship.</p>"},
                    {"title":"Agriculture and Industry","order_index":2,"content":"<h3>Agriculture and Industrialization</h3><p>Agriculture provides food, raw materials, employment (40%+ in Nigeria). <b>Challenges:</b> Low technology, poor storage, bad roads, climate dependence.</p><p><b>Industrialization:</b> Moving from agriculture to manufacturing. Import substitution vs export-led growth.</p>"},
                    {"title":"Population","order_index":3,"content":"<h3>Population</h3><p><b>Census:</b> Count of population. <b>Population pyramid:</b> Age/sex structure. <b>Overpopulation:</b> Resources can't sustain population. <b>Underpopulation:</b> Too few people for resources.</p><p><b>Malthusian theory:</b> Population grows exponentially, food grows arithmetically -> catastrophe unless checked.</p>"},
                    {"title":"International Organizations","order_index":4,"content":"<h3>Economic Organizations</h3><p><b>IMF:</b> International Monetary Fund -- loans to countries with balance of payments problems, conditions (austerity).</p><p><b>World Bank:</b> Long-term development loans, projects (roads, schools).</p><p><b>WTO:</b> World Trade Organization -- regulates international trade, settles disputes.</p><p><b>ECOWAS:</b> Economic Community of West African States -- regional integration, free movement, common currency goal.</p><p><b>OPEC:</b> Organization of Petroleum Exporting Countries -- coordinates oil production/pricing.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Government",
        "slug": "government",
        "category": "Social Sciences",
        "icon": "landmark",
        "color": "#9333EA",
        "description": "Complete WAEC/NECO/GCE/JAMB Government syllabus: Political concepts, constitutions, systems of government, political parties, elections, civil service, federalism, pre-colonial politics, colonialism, nationalism, international organizations",
        "lessons": [
            {
                "title": "Basic Concepts and Principles",
                "slug": "basic-concepts-and-principles",
                "summary": "Power, authority, legitimacy, sovereignty, democracy, rule of law, separation of powers, fundamental rights, political culture and socialization",
                "order_index": 1,
                "estimated_minutes": 300,
                "content": "<h2>Basic Concepts and Principles</h2><p>Before studying government, we must understand the foundational concepts. Power, authority, the state, and the principles that guide governance.</p>",
                "topics": [
                    {"title":"Basic Concepts","order_index":1,"content":"<h3>Power, Authority, Legitimacy, Sovereignty</h3><p><b>Power:</b> Ability to influence or compel others. <b>Authority:</b> Legitimate power (accepted as right). <b>Legitimacy:</b> Acceptance of government's right to rule. <b>Sovereignty:</b> Supreme power within a territory.</p><p><b>Types of authority (Weber):</b> Traditional (monarchy), Charismatic (personality), Legal-rational (constitution/law).</p>"},
                    {"title":"The State and Its Features","order_index":2,"content":"<h3>The State</h3><p><b>Features:</b> Population (people), Territory (defined land), Government (ruling body), Sovereignty (supreme power).</p><p><b>Difference from Nation:</b> State is political/legal; Nation is cultural/ethnic. Nigeria = state with 250+ nations within it.</p>"},
                    {"title":"Democracy","order_index":3,"content":"<h3>Democracy</h3><p>Government of the people, by the people, for the people. <b>Features:</b> Elections, rule of law, fundamental rights, periodic elections, multi-party system, separation of powers.</p><p><b>Types:</b> Direct (all vote on everything -- ancient Athens) and Representative (elect officials -- modern).</p>"},
                    {"title":"Rule of Law","order_index":4,"content":"<h3>Rule of Law (Dicey)</h3><p>(1) Supremacy of law -- no one is above the law. (2) Equality before the law. (3) Rights protected by courts, not abstract declarations.</p>"},
                    {"title":"Separation of Powers","order_index":5,"content":"<h3>Separation of Powers (Montesquieu)</h3><p><b>Legislature:</b> Makes laws (Parliament). <b>Executive:</b> Implements laws (President/Cabinet). <b>Judiciary:</b> Interprets laws (Courts).</p><p><b>Checks and balances:</b> Each branch checks the others. President vetoes, Courts declare unconstitutional, Legislature impeaches.</p>"},
                    {"title":"Fundamental Human Rights","order_index":6,"content":"<h3>Fundamental Rights</h3><p>Rights that belong to every person. <b>Examples:</b> Right to life, dignity, fair hearing, private/family life, freedom of thought/religion, expression, assembly, movement, freedom from discrimination.</p><p><b>Limitations:</b> Cannot be absolute -- must be balanced with public safety/national security.</p>"},
                    {"title":"Political Culture and Socialization","order_index":7,"content":"<h3>Political Culture and Socialization</h3><p><b>Political culture:</b> Attitudes, beliefs about politics. <b>Political socialization:</b> How people learn political values -- through family, school, media, peers, religion.</p><p><b>Types (Almond & Verba):</b> Parochial (unaware), Subject (aware but passive), Participant (active/civic).</p>"}
                ]
            },
            {
                "title": "Constitutions and Systems of Government",
                "slug": "constitutions-and-systems-of-government",
                "summary": "Types of constitutions, presidential vs parliamentary, unitary vs federal, organs of government, arms of government",
                "order_index": 2,
                "estimated_minutes": 240,
                "content": "<h2>Constitutions and Systems of Government</h2><p>The constitution is the supreme law. The system of government determines how power is distributed.</p>",
                "topics": [
                    {"title":"Constitutions","order_index":1,"content":"<h3>Constitutions</h3><p><b>Written vs Unwritten:</b> Written (codified, single document -- USA, Nigeria). Unwritten (customs, conventions, statutes -- UK).</p><p><b>Rigid vs Flexible:</b> Rigid (hard to amend, special majority). Flexible (easy to amend, ordinary majority).</p><p><b>Functions:</b> Distributing power, defining rights, establishing government structure, expressing national values.</p>"},
                    {"title":"Presidential System","order_index":2,"content":"<h3>Presidential vs Parliamentary</h3><p><b>Presidential:</b> President = head of state AND government. Separate from legislature. Fixed term. Example: USA, Nigeria.</p><p><b>Parliamentary:</b> Prime Minister = head of government. Monarch/President = ceremonial head. PM from parliament. Example: UK, India.</p>"},
                    {"title":"Unitary and Federal Systems","order_index":3,"content":"<h3>Unitary vs Federal</h3><p><b>Unitary:</b> Central government has all power. Local units derive authority from center. Example: UK, France, Ghana.</p><p><b>Federal:</b> Power divided between central and regional governments. Each has constitutional autonomy. Example: USA, Nigeria, India.</p><p><b>Nigeria:</b> 1999 Constitution established 36 states + FCT. Exclusive list (fed only), Concurrent list (both), Residual list (states).</p>"}
                ]
            },
            {
                "title": "Political Parties and Electoral Systems",
                "slug": "political-parties-and-electoral-systems",
                "summary": "Political parties, party systems, pressure groups, elections, electoral commissions, voting behavior",
                "order_index": 3,
                "estimated_minutes": 240,
                "content": "<h2>Political Parties and Elections</h2><p>Political parties aggregate interests and contest elections. Elections are the mechanism through which citizens choose leaders.</p>",
                "topics": [
                    {"title":"Political Parties","order_index":1,"content":"<h3>Political Parties</h3><p><b>Functions:</b> Aggregate interests, recruit leaders, contest elections, form government, educate public.</p><p><b>Party systems:</b> One-party (China, North Korea), Two-party (USA, UK), Multi-party (Nigeria, India, Germany).</p>"},
                    {"title":"Pressure Groups","order_index":2,"content":"<h3>Pressure Groups</h3><p>Organizations that influence government without contesting elections. NLC (labour), NACCIMA (commerce), ASUU (academics).</p><p><b>Methods:</b> Lobbying, strikes, protests, media campaigns, litigation.</p>"},
                    {"title":"Elections and Electoral Systems","order_index":3,"content":"<h3>Elections</h3><p><b>Types:</b> Primary (select party candidate), General (elect officials), By-election (fill vacancy).</p><p><b>Electoral systems:</b> First-past-the-post (FPTP) -- winner takes all. Proportional representation (PR) -- seats proportional to votes.</p><p><b>INEC (Independent National Electoral Commission):</b> Organizes and conducts elections in Nigeria. Must be independent.</p>"},
                    {"title":"Suffrage and Franchise","order_index":4,"content":"<h3>Suffrage</h3><p>Right to vote. Universal adult suffrage (18+ in Nigeria). <b>Limitations:</b> Non-citizens, unsound mind, convicted criminals, undischarged bankrupts.</p>"}
                ]
            },
            {
                "title": "Civil Service and Public Administration",
                "slug": "civil-service-and-public-administration",
                "summary": "Civil service structure, functions, characteristics, problems, public corporations, local government",
                "order_index": 4,
                "estimated_minutes": 180,
                "content": "<h2>Civil Service and Public Administration</h2><p>The civil service implements government policies. Bureaucracy is the machinery of government.</p>",
                "topics": [
                    {"title":"Civil Service","order_index":1,"content":"<h3>Civil Service</h3><p>Permanent, professional, neutral body that implements government policies.</p><p><b>Characteristics:</b> Permanence, neutrality, anonymity, merit-based, hierarchy, specialization.</p><p><b>Functions:</b> Advise ministers, implement policies, prepare budget, collect data, administer programs.</p><p><b>Problems:</b> Red tape, corruption, inefficiency, political interference, low morale.</p>"},
                    {"title":"Public Corporations","order_index":2,"content":"<h3>Public Corporations</h3><p>Government-owned enterprises providing essential services. NPA (ports), NITEL (telecom), NEPA/PHCN (electricity).</p><p><b>Problems:</b> Inefficiency, political interference, overstaffing, corruption. Many have been privatized.</p>"},
                    {"title":"Local Government","order_index":3,"content":"<h3>Local Government</h3><p>Third tier of government in Nigeria (774 LGAs). <b>Functions:</b> Primary education, primary health, markets, sanitation, registration, local roads.</p>"}
                ]
            },
            {
                "title": "Pre-Colonial and Colonial Political Systems",
                "slug": "pre-colonial-and-colonial-political-systems",
                "summary": "Pre-colonial political systems in West Africa, colonial administration, indirect rule, assimilation, nationalism, constitutional developments",
                "order_index": 5,
                "estimated_minutes": 300,
                "content": "<h2>Pre-Colonial and Colonial Political Systems</h2><p>Before Europeans arrived, West Africa had sophisticated political systems. Colonialism disrupted them and sowed the seeds of today's states.</p>",
                "topics": [
                    {"title":"Pre-Colonial Political Systems","order_index":1,"content":"<h3>Pre-Colonial Nigeria</h3><p><b>Hausa/Fulani:</b> Emirate system. Emir = absolute ruler. Council of elders. Islamic law. Centralized, theocratic.</p><p><b>Yoruba:</b> Oba (king) with checks and balances. Oyomesi (kingmakers), Ogboni (secret society). Could destool Oba. Decentralized checks.</p><p><b>Igbo:</b> Stateless/acephalous. No kings. Village republics. Council of elders. Age grades. Decentralized democracy.</p>"},
                    {"title":"British Colonial Administration","order_index":2,"content":"<h3>Indirect Rule (Lugard)</h3><p>British ruled through traditional chiefs. <b>Success in North:</b> Emirate system already centralized. <b>Failure in East:</b> Igbo had no chiefs; warrant chiefs were artificial and resented.</p>"},
                    {"title":"French Colonial Administration","order_index":3,"content":"<h3>Assimilation and Association</h3><p><b>Assimilation:</b> Make Africans French (in culture, language, citizenship). Limited to four communes (Dakar, St. Louis, etc.).</p><p><b>Association:</b> Later policy. Accept African difference, govern indirectly but French control remained.</p>"},
                    {"title":"Nationalism in West Africa","order_index":4,"content":"<h3>Nationalism</h3><p>Movement for independence. <b>Pre-WWII (proto-nationalism):</b> Early resistance, educated elite demanded reforms. National Congress of British West Africa (1920).</p><p><b>Post-WWII:</b> Much stronger. Factors: War weakened Europe, Atlantic Charter, educated elite (Nnamdi Azikiwe, Kwame Nkrumah), newspapers, labor movements.</p><p><b>Key figures:</b> Nigeria: Nnamdi Azikiwe, Obafemi Awolowo, Ahmadu Bello, Tafawa Balewa. Ghana: Kwame Nkrumah. Sierra Leone: Siaka Stevens.</p>"},
                    {"title":"Constitutional Developments in Nigeria","order_index":5,"content":"<h3>Nigeria's Constitutions</h3><p><b>Clifford Constitution (1922):</b> First written constitution. Elected members introduced. <b>Richards (1946):</b> Regionalism introduced (North, East, West). <b>Macpherson (1951):</b> More Nigerian participation, central legislature.</p><p><b>Lyttleton (1954):</b> True federalism. <b>Independence (1960):</b> Parliamentary system, Queen as head of state. Governor-General. <b>Republican (1963):</b> Became a republic. President replaced Governor-General.</p><p><b>1979 Constitution:</b> Presidential system (US-style). <b>1989 Constitution:</b> Two-party system (SDP, NRC). <b>1999 Constitution:</b> Current. Presidential, 36 states, FCT Abuja.</p>"}
                ]
            },
            {
                "title": "Military Rule and International Relations",
                "slug": "military-rule-and-international-relations",
                "summary": "Military intervention in politics, coups in Nigeria, foreign policy, international organizations (UN, AU, Commonwealth, ECOWAS)",
                "order_index": 6,
                "estimated_minutes": 240,
                "content": "<h2>Military Rule and International Relations</h2><p>Nigeria has experienced long periods of military rule. How do countries relate to each other on the global stage?</p>",
                "topics": [
                    {"title":"Military Rule in Nigeria","order_index":1,"content":"<h3>Coups in Nigeria</h3><p><b>1966:</b> First coup (Major Nzeogwu). Ironsi took over. Counter-coup: Gowon. <b>1975:</b> Murtala Mohammed (coup of 'clean-up'). <b>1976:</b> Dimka coup (Murtala killed). Obasanjo.</p><p><b>1983:</b> Buhari overthrew Shagari. <b>1985:</b> Babangida overthrew Buhari. <b>1993:</b> Abacha. <b>1998:</b> Abubakar. Transition to democracy in 1999.</p><p><b>Reasons for coups:</b> Corruption, economic mismanagement, rigged elections, personal ambition.</p>"},
                    {"title":"Nigeria's Foreign Policy","order_index":2,"content":"<h3>Nigeria's Foreign Policy</h3><p><b>Principles:</b> Africa as centerpiece, non-alignment, peaceful dispute resolution, economic diplomacy, respect for sovereignty.</p><p><b>Afrocentric policy:</b> Decolonization of Africa, anti-apartheid (huge role in freeing South Africa), peacekeeping (ECOMOG, UN).</p>"},
                    {"title":"International Organizations","order_index":3,"content":"<h3>Key Organizations</h3><p><b>United Nations (UNO):</b> Maintain peace. GA (all members), Security Council (5 permanent + 10 rotating), ICJ, Secretariat. Nigeria active in peacekeeping.</p><p><b>African Union (AU):</b> Originally OAU (1963). Promotes unity, development, peace in Africa.</p><p><b>Commonwealth:</b> Former British colonies. Promotes democracy, development. Nigeria suspended 1995-1999 (Abacha era).</p><p><b>ECOWAS:</b> 15 West African states. Free movement, trade, peacekeeping (ECOMOG in Liberia, Sierra Leone).</p>"}
                ]
            }
        ]
    },
    {
        "name": "Literature in English",
        "slug": "literature-in-english",
        "category": "Arts and Humanities",
        "icon": "book",
        "color": "#8B5CF6",
        "description": "Complete WAEC/NECO/GCE/JAMB Literature-in-English syllabus: Prose, poetry, drama, literary appreciation, figures of speech, African and non-African literature, Shakespeare, poetic devices",
        "lessons": [
            {
                "title": "Introduction to Literature",
                "slug": "introduction-to-literature",
                "summary": "Definition of literature, genres, functions of literature, literary appreciation basics",
                "order_index": 1,
                "estimated_minutes": 180,
                "content": "<h2>Introduction to Literature</h2><p>Literature is the mirror of life. It uses words to create art, explore human experience, and reflect society.</p>",
                "topics": [
                    {"title":"What is Literature?","order_index":1,"content":"<h3>What is Literature?</h3><p>Creative writing of artistic value. <b>Functions:</b> Entertainment, education, social commentary, cultural preservation, moral instruction, emotional catharsis.</p><p><b>Genres:</b> Prose (fiction/non-fiction), Poetry (verse), Drama (performance). Each has unique conventions and techniques.</p>"}
                ]
            },
            {
                "title": "Prose",
                "slug": "prose",
                "summary": "Elements of prose, characterization, plot, setting, theme, narrative techniques, types of prose",
                "order_index": 2,
                "estimated_minutes": 240,
                "content": "<h2>Prose</h2><p>Prose is ordinary written language. Fiction tells imagined stories. Non-fiction tells true ones.</p>",
                "topics": [
                    {"title":"Elements of Prose","order_index":1,"content":"<h3>Elements of Prose</h3><p><b>Plot:</b> Sequence of events. Exposition, rising action, climax, falling action, resolution.</p><p><b>Characterization:</b> Protagonist (main character), Antagonist (opposes protagonist). Round (complex) vs Flat (simple). Static (unchanging) vs Dynamic (changes).</p><p><b>Setting:</b> Time and place. <b>Theme:</b> Central idea/message. <b>Point of view:</b> First person (I), Third person limited (he/she, one character's thoughts), Omniscient (all-knowing).</p>"},
                    {"title":"Types of Prose","order_index":2,"content":"<h3>Types of Prose</h3><p><b>Novel:</b> Long fictional narrative. <b>Novella:</b> Shorter than novel. <b>Short story:</b> Single effect, few characters. <b>Fable:</b> Moral lesson, animals as characters. <b>Biography/Autobiography:</b> Life story.</p>"}
                ]
            },
            {
                "title": "Poetry",
                "slug": "poetry",
                "summary": "Types of poetry, rhyme, meter, poetic devices, imagery, symbolism, tone, mood",
                "order_index": 3,
                "estimated_minutes": 240,
                "content": "<h2>Poetry</h2><p>Poetry is the most concentrated form of literature. Every word counts, sound and sense work together.</p>",
                "topics": [
                    {"title":"Elements of Poetry","order_index":1,"content":"<h3>Elements of Poetry</h3><p><b>Rhyme:</b> Repetition of sounds at line ends (ABAB, AABB). <b>Rhythm/Meter:</b> Pattern of stressed/unstressed syllables.</p><p><b>Iambic pentameter:</b> da-DUM x5 (Shakespeare). <b>Stanza:</b> Group of lines (couplet=2, quatrain=4, sestet=6, octave=8).</p>"},
                    {"title":"Poetic Devices","order_index":2,"content":"<h3>Poetic Devices</h3><p><b>Simile:</b> Comparison using 'like' or 'as'. <b>Metaphor:</b> Direct comparison. <b>Personification:</b> Human qualities to objects. <b>Hyperbole:</b> Exaggeration. <b>Irony:</b> Opposite of literal. <b>Alliteration:</b> Same initial sounds. <b>Assonance:</b> Repeated vowel sounds. <b>Onomatopoeia:</b> Sound words (buzz, hiss). <b>Imagery:</b> Vivid sensory language.</p>"},
                    {"title":"Types of Poetry","order_index":3,"content":"<h3>Types of Poetry</h3><p><b>Lyric:</b> Personal emotion, musical. <b>Narrative:</b> Tells a story. <b>Sonnet:</b> 14 lines, specific rhyme scheme. Shakespearean or Petrarchan.</p><p><b>Elegy:</b> Poem of mourning. <b>Ode:</b> Praise poem. <b>Ballad:</b> Storytelling song. <b>Epic:</b> Long heroic narrative (Homer, Milton).</p>"}
                ]
            },
            {
                "title": "Drama",
                "slug": "drama",
                "summary": "Elements of drama, tragedy, comedy, tragicomedy, dialogue, soliloquy, aside, stage directions",
                "order_index": 4,
                "estimated_minutes": 240,
                "content": "<h2>Drama</h2><p>Drama is literature written to be performed. The play is the thing!</p>",
                "topics": [
                    {"title":"Elements of Drama","order_index":1,"content":"<h3>Elements of Drama</h3><p><b>Acts and Scenes:</b> Divisions of the play. <b>Dialogue:</b> Character speech. <b>Soliloquy:</b> Speaking alone (reveals thoughts). <b>Aside:</b> Private remark to audience. <b>Stage directions:</b> Instructions for performance.</p><p><b>Tragedy:</b> Hero's downfall (often due to tragic flaw/hubris). Catharsis (emotional purging). <b>Comedy:</b> Light, humorous, happy ending. <b>Tragicomedy:</b> Mix of both.</p>"}
                ]
            },
            {
                "title": "Literary Appreciation and Criticism",
                "slug": "literary-appreciation-and-criticism",
                "summary": "How to read literature critically, identifying themes, analyzing style, context, literary periods, African literature",
                "order_index": 5,
                "estimated_minutes": 180,
                "content": "<h2>Literary Appreciation</h2><p>Go beyond 'I like it' to 'WHY does it work?' Critical appreciation is the heart of literature exams.</p>",
                "topics": [
                    {"title":"How to Appreciate Literature","order_index":1,"content":"<h3>Literary Appreciation</h3><p><b>Questions to ask:</b> What is the theme? How is language used? What is the tone/mood? How is the work structured? What context (historical/social) influenced it?</p><p><b>Context matters:</b> African literature reflects colonial experience, post-colonial identity, traditional culture vs modernity.</p><p><b>Major African writers:</b> Chinua Achebe (Things Fall Apart), Wole Soyinka (The Lion and the Jewel, Kongi's Harvest), Ngugi wa Thiong'o, Ayi Kwei Armah, Ama Ata Aidoo, Bessie Head.</p>"},
                    {"title":"Shakespeare","order_index":2,"content":"<h3>Shakespeare</h3><p>Regularly featured in WAEC/NECO. <b>Key works:</b> Romeo and Juliet, Julius Caesar, Othello, The Merchant of Venice, Macbeth, Hamlet.</p><p><b>Understanding Shakespeare:</b> Read footnotes for archaic words. Pay attention to soliloquies. Watch for recurring imagery/themes. Know the main characters and their roles.</p>"}
                ]
            }
        ]
    },
    {
        "name": "History",
        "slug": "history",
        "category": "Arts and Humanities",
        "icon": "scroll",
        "color": "#B45309",
        "description": "Complete WAEC/NECO/GCE/JAMB History syllabus: Nigerian history from pre-colonial to present, West African history, major empires, colonialism, nationalism, independence, civil war, and contemporary developments",
        "lessons": [
            {
                "title": "Pre-Colonial West African History",
                "slug": "pre-colonial-west-african-history",
                "summary": "Early civilizations, Trans-Saharan trade, empires of Ghana, Mali, Songhai, Kanem-Borno, Hausa states, Oyo, Benin, Igbo",
                "order_index": 1,
                "estimated_minutes": 300,
                "content": "<h2>Pre-Colonial West African History</h2><p>Africa was not 'without history' before colonialism. Great empires flourished: Ghana, Mali, Songhai, Oyo, Benin, Kanem-Borno.</p>",
                "topics": [
                    {"title":"Ancient West African Empires","order_index":1,"content":"<h3>Ghana, Mali, Songhai</h3><p><b>Ghana Empire (300-1200 AD):</b> 'Land of Gold'. Taxed Trans-Saharan trade. Displaced by Almoravids.</p><p><b>Mali Empire (1235-1600):</b> Sundiata Keita founded. Mansa Musa's pilgrimage to Mecca (1324) showed Mali's wealth. Timbuktu -- center of learning (University of Sankore).</p><p><b>Songhai Empire (1464-1591):</b> Sunni Ali, Askia Muhammad. Largest of the three. Fell to Moroccan invasion (gunpowder vs spears).</p>"},
                    {"title":"Trans-Saharan Trade","order_index":2,"content":"<h3>Trans-Saharan Trade</h3><p>North Africa exchanged salt, horses, cloth, books for West African gold, slaves, kola nuts. Made empires wealthy. Brought Islam to West Africa.</p>"},
                    {"title":"Oyo Empire","order_index":3,"content":"<h3>Oyo Empire (1400-1835)</h3><p>Yoruba empire. Powerful cavalry. Alafin (king) with Oyomesi (kingmakers) and Ogboni checks. Collapsed due to internal conflicts and Fulani jihad.</p>"},
                    {"title":"Benin Empire","order_index":4,"content":"<h3>Benin Empire</h3><p>Edo people (Nigeria). Famous for bronze/ivory art. Oba (divine king). Flourished 15th-19th century. Destroyed by British Punitive Expedition (1897).</p>"},
                    {"title":"Kanem-Borno Empire","order_index":5,"content":"<h3>Kanem-Borno</h3><p>Lake Chad region. Lasted 1000+ years (8th-19th century). Islamic state. Trade across Sahara. Seifawa dynasty. Sayfawa dynasty ended in 1846.</p>"},
                    {"title":"Hausa States","order_index":6,"content":"<h3>Hausa Bakwai (Seven States)</h3><p>Biram, Daura, Katsina, Kano, Rano, Gobir, Zaria. City-states, independent but linked by culture/language. Trans-Saharan trade. Later conquered by Usman dan Fodio's jihad (1804).</p>"}
                ]
            },
            {
                "title": "Colonial Nigeria",
                "slug": "colonial-nigeria",
                "summary": "European colonization, Berlin Conference, British conquest, Lugard's amalgamation, colonial economy, impact of colonialism",
                "order_index": 2,
                "estimated_minutes": 240,
                "content": "<h2>Colonial Nigeria</h2><p>The British colonized what became Nigeria through conquest, treaties, and trickery. Understanding colonialism is essential to understanding modern Nigeria.</p>",
                "topics": [
                    {"title":"The Scramble for Africa","order_index":1,"content":"<h3>Berlin Conference (1884-1885)</h3><p>European powers divided Africa. No African present. Effective occupation principle. Nigeria assigned to Britain.</p>"},
                    {"title":"British Conquest","order_index":2,"content":"<h3>British Conquest of Nigeria</h3><p><b>Lagos:</b> Annexed 1861 (bombarded by Consul Freeman). <b>Niger Coast Protectorate:</b> 1891. <b>Royal Niger Company:</b> Under George Goldie. <b>Benin:</b> Punitive Expedition 1897. <b>Aro Confederacy:</b> Defeated 1901-1902. <b>Northern Nigeria:</b> Lugard conquered 1903 (Sokoto, Kano).</p>"},
                    {"title":"Amalgamation of 1914","order_index":3,"content":"<h3>Amalgamation 1914</h3><p>Lord Lugard merged Northern and Southern Nigeria for administrative convenience and economy. Created Nigeria. North = protectorate, South = colony and protectorate.</p>"},
                    {"title":"Colonial Economy","order_index":4,"content":"<h3>Colonial Economy</h3><p>Nigeria as source of raw materials: palm oil, groundnuts, cocoa, cotton, tin, coal. Railways built to transport goods. Cash crops over food crops. Native authorities collected taxes.</p>"}
                ]
            },
            {
                "title": "Nigerian Independence and Post-Colonial Era",
                "slug": "nigerian-independence-and-post-colonial-era",
                "summary": "Nationalism, independence, First Republic, military coups, civil war, Second Republic, Fourth Republic, contemporary Nigeria",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Nigerian Independence and Post-Colonial Era</h2><p>Nigeria gained independence in 1960. The journey since has been turbulent -- coups, civil war, democracy, and ongoing challenges.</p>",
                "topics": [
                    {"title":"Nationalist Movement","order_index":1,"content":"<h3>Nationalism in Nigeria</h3><p><b>Early nationalists:</b> Herbert Macaulay (father of Nigerian nationalism), Nnamdi Azikiwe (Zik), Obafemi Awolowo, Ahmadu Bello, Tafawa Balewa, Anthony Enahoro (moved independence motion 1953).</p><p><b>Parties:</b> NCNC (Zik, Igbo-dominated), Action Group (Awolowo, Yoruba), NPC (Bello, Sardauna of Sokoto, Hausa-Fulani). Regionalism defined politics.</p>"},
                    {"title":"Independence and First Republic","order_index":2,"content":"<h3>Independence (1960-1966)</h3><p>October 1, 1960. PM Tafawa Balewa. Governor-General Nnamdi Azikiwe. Republican 1963 (Azikiwe President). Regional governments: North (Bello/Sardauna), West (Awolowo), East (Okpara). Political crises, census dispute, election rigging 1964-65.</p>"},
                    {"title":"Military Coups 1966","order_index":3,"content":"<h3>First Coup (Jan 1966)</h3><p>Major Nzeogwu and young officers killed Balewa, Bello, Okotie-Eboh, Akintola. Ironsi took over. Unitarism decree 34 (abolished federalism). Anti-Igbo backlash.</p><p><b>Counter-coup (July 1966):</b> Northern officers killed Ironsi. Gowon became head of state.</p>"},
                    {"title":"Nigerian Civil War (1967-1970)","order_index":4,"content":"<h3>Biafran War</h3><p>May 1967: Ojukwu declared Republic of Biafra (Eastern region). Gowon 'police action' turned into 30-month war. 1-3 million died (mostly starvation). 'No victor, no vanquished' -- Gowon's reconciliation speech.</p>"},
                    {"title":"Oil Era and Military Rule","order_index":5,"content":"<h3>Oil Boom and Military Rule (1970s-1990s)</h3><p>Oil money transformed Nigeria. Gowon (1966-1975), Murtala (1975-1976, assassinated), Obasanjo (1976-1979, transition to democracy).</p><p><b>Second Republic (1979-1983):</b> Shehu Shagari (NPN). 19 states. Oil prices crashed 1981. Corruption. Coup 1983 (Buhari).</p><p><b>Babangida (1985-1993):</b> SAP (Structural Adjustment Program). June 12, 1993 election (Abiola won, annulled). 'Democracy has no skeleton' -- MKO Abiola.</p><p><b>Abacha (1993-1998):</b> Most brutal. Ken Saro-Wiwa executed. Abiola died in detention. Transition Abubakar 1998-1999.</p>"},
                    {"title":"Fourth Republic (1999-Present)","order_index":6,"content":"<h3>Fourth Republic</h3><p>Obasanjo (1999-2007, 2 terms). Yar'Adua (2007-2010, died). Jonathan (2010-2015, Goodluck). Buhari (2015-2023). Tinubu (2023-present). Challenges: corruption, insecurity, Boko Haram, banditry, economic issues, restructuring debate.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Christian Religious Studies (CRS)",
        "slug": "christian-religious-studies",
        "category": "Arts and Humanities",
        "icon": "church",
        "color": "#DC2626",
        "description": "Complete WAEC/NECO/GCE/JAMB CRS syllabus: Old Testament history, creation, patriarchs, exodus, monarchy, prophets; New Testament life of Jesus, parables, miracles, early church, Paul's epistles; biblical themes and moral teachings",
        "lessons": [
            {
                "title": "The Old Testament",
                "slug": "the-old-testament",
                "summary": "Creation, Adam to Noah, Abraham, Isaac, Jacob, Joseph, Moses, Exodus, Ten Commandments, Judges, Kings, Prophets",
                "order_index": 1,
                "estimated_minutes": 360,
                "content": "<h2>The Old Testament</h2><p>The Old Testament tells the story of God's relationship with humanity and Israel. From creation to the prophets calling for justice.</p>",
                "topics": [
                    {"title":"Creation and the Patriarchs","order_index":1,"content":"<h3>Creation to Abraham</h3><p><b>Creation (Genesis 1-2):</b> God created heaven, earth, light, plants, animals, humans (in His image). Six days, rested on 7th.</p><p><b>The Fall (Genesis 3):</b> Adam and Eve disobeyed. Sin entered the world.</p><p><b>Noah (Genesis 6-9):</b> Flood, God's covenant with Noah (rainbow). <b>Tower of Babel:</b> Human pride, languages confused.</p><p><b>Abraham (Genesis 12-25):</b> God's call: 'Go from your country...' Covenant: descendants, land, blessing. Faith tested (Isaac). Father of Judaism, Christianity, Islam.</p><p><b>Isaac, Jacob, Joseph:</b> Jacob->12 sons (12 tribes). Joseph sold into Egypt, rose to power, saved family from famine.</p>"},
                    {"title":"Moses and the Exodus","order_index":2,"content":"<h3>Moses and the Exodus</h3><p><b>Moses:</b> Born in Egypt, raised in palace, fled to Midian, called by God (burning bush). Plagues on Egypt. Passover.</p><p><b>Exodus:</b> Crossing Red Sea. Wilderness: manna, water from rock. <b>Ten Commandments (Exodus 20):</b> Worship only God, no idols, don't misuse God's name, Sabbath, honor parents, no murder, adultery, theft, false witness, coveting.</p><p><b>Wandering 40 years:</b> Because of disobedience. Moses died in Moab, Joshua led into Canaan.</p>"},
                    {"title":"The Judges and The United Monarchy","order_index":3,"content":"<h3>Judges to United Kingdom</h3><p><b>Judges:</b> Deborah, Gideon, Samson, Samuel. Cyclical pattern: sin -> oppression -> cry -> judge delivers.</p><p><b>Saul:</b> First king. Disobeyed God, rejected. <b>David:</b> Man after God's heart. Killed Goliath. Established Jerusalem. God's covenant: throne forever (messianic).</p><p><b>Solomon:</b> Wisdom. Built Temple. But many wives led to idolatry. Kingdom divided after his death: North (Israel) and South (Judah).</p>"},
                    {"title":"The Prophets","order_index":4,"content":"<h3>Prophets</h3><p>Called people back to God. <b>Elijah:</b> Challenged Baal prophets. <b>Isaiah:</b> Messianic prophecies. <b>Jeremiah:</b> Weeping prophet, fall of Jerusalem. <b>Ezekiel:</b> Vision of dry bones.</p><p><b>Minor prophets:</b> Hosea (God's unfailing love), Amos (social justice), Jonah (God's mercy to all nations).</p><p><b>Key themes:</b> Repentance, social justice, faithfulness to God, messianic hope.</p>"}
                ]
            },
            {
                "title": "The New Testament",
                "slug": "the-new-testament",
                "summary": "Life of Jesus Christ, parables, miracles, beatitudes, passion, resurrection, the early church, Paul's missionary journeys, epistles",
                "order_index": 2,
                "estimated_minutes": 360,
                "content": "<h2>The New Testament</h2><p>The New Testament is the story of Jesus Christ and the early church. It fulfills Old Testament prophecies and establishes a new covenant.</p>",
                "topics": [
                    {"title":"Life of Jesus Christ","order_index":1,"content":"<h3>Jesus: Birth to Ministry</h3><p><b>Annunciation:</b> Gabriel to Mary. <b>Birth:</b> Bethlehem. Shepherds, Wise Men. <b>Presentation in Temple:</b> Simeon and Anna.</p><p><b>Baptism:</b> John the Baptist. Voice from heaven: 'This is my beloved Son.' <b>Temptation:</b> 40 days in wilderness, Satan tempted.</p><p><b>Disciples:</b> 12 called (Peter, James, John, etc.). <b>Sermon on the Mount:</b> Beatitudes (Blessed are the poor in spirit...). Lord's Prayer.</p>"},
                    {"title":"Parables and Miracles","order_index":2,"content":"<h3>Parables and Miracles</h3><p><b>Parables:</b> Earthly stories with heavenly meanings. Prodigal Son (God's forgiveness), Good Samaritan (love your neighbor), Sower (reception of word), Lost Sheep, Mustard Seed.</p><p><b>Miracles:</b> Water to wine, healing blind/bedridden/lepers, feeding 5000, walking on water, raising Lazarus. Purpose: Show divine power, build faith, demonstrate compassion.</p>"},
                    {"title":"Passion and Resurrection","order_index":3,"content":"<h3>Passion Week</h3><p><b>Triumphal entry:</b> Palm Sunday. <b>Last Supper:</b> Institution of Holy Communion. <b>Betrayal:</b> Judas 30 pieces of silver. <b>Trial:</b> Before Caiaphas, Pilate. <b>Crucifixion:</b> Calvary/Golgotha.</p><p><b>Resurrection:</b> Third day. Empty tomb. Appearances to Mary Magdalene, disciples, Thomas, 500+. <b>Ascension:</b> 40 days after resurrection.</p><p><b>Significance:</b> Atonement for sin, victory over death, assurance of eternal life.</p>"},
                    {"title":"The Early Church","order_index":4,"content":"<h3>Acts of the Apostles</h3><p><b>Pentecost:</b> Holy Spirit came (tongues of fire). Peter's sermon: 3000 converted.</p><p><b>Early church:</b> Communal living (shared possessions). Persecution: Stephen stoned, Saul (later Paul) persecuted.</p><p><b>Peter's ministry:</b> Cornelius (Gentiles accepted). <b>Paul's conversion:</b> Damacus road. 3 missionary journeys (Asia Minor, Greece).</p>"},
                    {"title":"Paul's Epistles","order_index":5,"content":"<h3>Letters of Paul</h3><p><b>Romans:</b> Justification by faith. <b>1&2 Corinthians:</b> Church problems, love chapter (13). <b>Galatians:</b> Faith vs law. <b>Ephesians:</b> Unity in Christ. <b>Philippians:</b> Joy in suffering. <b>1&2 Thessalonians:</b> Second coming.</p><p><b>Pastoral epistles:</b> 1&2 Timothy, Titus (church leadership). <b>Philemon:</b> Reconciliation. <b>Key themes:</b> Grace, faith, love, unity, Christian living, hope.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Civic Education",
        "slug": "civic-education",
        "category": "Social Sciences",
        "icon": "shield",
        "color": "#0D9488",
        "description": "Complete WAEC/NECO/GCE/JAMB Civic Education syllabus: Citizenship, rights and duties, government institutions, rule of law, democracy, human rights, responsible parenting, drug abuse, traffic regulations, inter-personal relations",
        "lessons": [
            {
                "title": "Citizenship and Rights",
                "slug": "citizenship-and-rights",
                "summary": "Meaning of citizenship, types, rights and duties of citizens, fundamental human rights, Nigerian constitution",
                "order_index": 1,
                "estimated_minutes": 240,
                "content": "<h2>Citizenship and Rights</h2><p>Being a citizen comes with rights AND responsibilities. A good citizen knows both.</p>",
                "topics": [
                    {"title":"Citizenship","order_index":1,"content":"<h3>Citizenship</h3><p><b>Citizenship by birth:</b> Born in Nigeria OR parents are Nigerian. <b>Citizenship by registration:</b> Non-Nigerian married to Nigerian (15+ years), or special circumstances.</p><p><b>Citizenship by naturalization:</b> Foreigner lives 15+ years, good character, takes oath. <b>Dual citizenship:</b> Nigeria allows (unlike some countries).</p><p><b>Rights:</b> Life, dignity, fair hearing, privacy, freedom of thought/religion/expression/assembly/movement, freedom from discrimination.</p><p><b>Duties:</b> Pay taxes, obey laws, vote, defend Nigeria, serve in jury, protect public property.</p>"},
                    {"title":"Fundamental Human Rights","order_index":2,"content":"<h3>Fundamental Human Rights (Chapter IV, 1999 Constitution)</h3><p>Right to life (not deprived intentionally), dignity of human person (no torture/slavery), personal liberty, fair hearing, private/family life, freedom of thought/conscience/religion, expression/press, peaceful assembly, movement, freedom from discrimination.</p><p><b>Limitations:</b> Rights can be limited for public safety, public order, public morality, or national security.</p><p><b>Enforcement:</b> High Court. Legal aid for poor. Fundamental Rights Enforcement Procedure Rules.</p>"}
                ]
            },
            {
                "title": "Government and Democracy",
                "slug": "government-and-democracy",
                "summary": "Types of government, democracy, rule of law, separation of powers, federalism, Nigerian government structure",
                "order_index": 2,
                "estimated_minutes": 240,
                "content": "<h2>Government and Democracy</h2><p>Understanding how government works makes you an effective citizen.</p>",
                "topics": [
                    {"title":"Democracy and Rule of Law","order_index":1,"content":"<h3>Democracy</h3><p>Government by the people. <b>Features:</b> Regular elections, rule of law, multi-party, fundamental rights, independent judiciary, free press, civil society.</p><p><b>Limitations of democracy:</b> Slow decision-making, tyranny of majority, expensive elections, manipulation by rich/powerful.</p>"},
                    {"title":"Nigerian Government Structure","order_index":2,"content":"<h3>Nigeria's Government</h3><p><b>Executive:</b> President (head of state & government), Vice President, Ministers, govt agencies. <b>Legislature:</b> National Assembly (Senate + House of Reps). Makes laws. <b>Judiciary:</b> Supreme Court, Court of Appeal, High Courts, Sharia/Customary Courts.</p><p><b>Levels:</b> Federal, State (36 states + FCT), Local (774 LGAs). Exclusive, Concurrent, Residual lists.</p>"}
                ]
            },
            {
                "title": "Social Issues and Values",
                "slug": "social-issues-and-values",
                "summary": "Drug abuse, HIV/AIDS, traffic regulations, corruption, cultism, responsible parenting, inter-personal relations, values",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Social Issues and Values</h2><p>Good citizenship means engaging with real social problems and living by positive values.</p>",
                "topics": [
                    {"title":"Drug Abuse","order_index":1,"content":"<h3>Drug Abuse</h3><p>Illegal or excessive use of drugs. <b>Common drugs:</b> Cannabis (Indian hemp), cocaine, heroin, tramadol, codeine, methamphetamine (mkpuru mmiri).</p><p><b>Causes:</b> Peer pressure, curiosity, frustration, poverty, availability, unemployment, family problems.</p><p><b>Effects:</b> Health damage (mental, physical), addiction, crime, poverty, family breakdown, death. <b>NDLEA:</b> National Drug Law Enforcement Agency.</p>"},
                    {"title":"HIV/AIDS and STDs","order_index":2,"content":"<h3>HIV/AIDS</h3><p>Human Immunodeficiency Virus. Attacks immune system. Leads to AIDS (Acquired Immune Deficiency Syndrome).</p><p><b>Transmission:</b> Unprotected sex, blood transfusion, sharing needles, mother to child (during birth/breastfeeding).</p><p><b>Prevention:</b> Abstinence, condoms, faithful partnership, avoid sharing needles, blood screening, ART (antiretroviral therapy).</p>"},
                    {"title":"Traffic Regulations","order_index":3,"content":"<h3>Traffic Regulations</h3><p><b>FRSC:</b> Federal Road Safety Corps. Enforces traffic laws.</p><p>Speed limits, seat belts, no drink-driving, valid license, road signs, vehicle roadworthiness, no phone while driving, zebra crossing.</p>"},
                    {"title":"Cultism","order_index":4,"content":"<h3>Secret Cults</h3><p>Illegal secret societies (tertiary institutions). <b>Examples:</b> Buccaneers, Eiye, Neo-Black Movement. <b>Causes:</b> Peer pressure, protection, status, power.</p><p><b>Effects:</b> Violence, death, expulsion, criminal record, fear on campus. Solutions: Campus security, counseling, student engagement, strict laws.</p>"},
                    {"title":"Corruption","order_index":5,"content":"<h3>Corruption</h3><p>Dishonest or illegal behavior by people in power. <b>Types:</b> Bribery, embezzlement, nepotism, fraud, extortion, money laundering.</p><p><b>Effects:</b> Poor services, wasted resources, inequality, distrust, foreign disinvestment. <b>EFCC:</b> Economic and Financial Crimes Commission. <b>ICPC:</b> Independent Corrupt Practices Commission.</p>"},
                    {"title":"Values and Responsible Living","order_index":6,"content":"<h3>Values</h3><p>Principles guiding behavior. <b>Positive values:</b> Honesty, integrity, respect, hard work, discipline, patriotism, tolerance, contentment, justice.</p><p><b>Responsible parenting:</b> Provision, protection, education, moral training, love, discipline (not abuse). Good parenting = good citizens.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Commerce",
        "slug": "commerce",
        "category": "Business Studies",
        "icon": "shopping-bag",
        "color": "#2563EB",
        "description": "Complete WAEC/NECO/GCE/JAMB Commerce syllabus: Trade, buying and selling, retail and wholesale trade, advertising, transportation, communication, banking, insurance, import and export trade, business units, entrepreneurship",
        "lessons": [
            {
                "title": "Introduction to Commerce",
                "slug": "introduction-to-commerce",
                "summary": "Meaning and scope of commerce, functions of commerce, branches of commerce, production and factors of production",
                "order_index": 1,
                "estimated_minutes": 180,
                "content": "<h2>Introduction to Commerce</h2><p>Commerce is the distribution of goods and services. It connects producers to consumers. Without commerce, there is no economy.</p>",
                "topics": [
                    {"title":"What is Commerce?","order_index":1,"content":"<h3>Meaning of Commerce</h3><p>All activities involved in the distribution of goods and services from producers to consumers. <b>Commerce = Trade + Aids to trade.</b></p><p><b>Branches:</b> Trade (home and foreign), Transportation, Warehousing, Insurance, Banking, Advertising, Communication.</p><p><b>Production:</b> Creation of utility. Primary (farming, mining), Secondary (manufacturing), Tertiary (services).</p>"},
                    {"title":"Factors of Production","order_index":2,"content":"<h3>Factors of Production</h3><p><b>Land:</b> Natural resources. Reward = Rent. <b>Labor:</b> Human effort. Reward = Wages/Salary.</p><p><b>Capital:</b> Man-made resources. Reward = Interest. <b>Entrepreneur:</b> Organizer, risk-taker. Reward = Profit.</p>"}
                ]
            },
            {
                "title": "Trade",
                "slug": "trade",
                "summary": "Home trade, wholesale and retail, types of retailers, functions of wholesalers, modern retailing, e-commerce, foreign trade",
                "order_index": 2,
                "estimated_minutes": 300,
                "content": "<h2>Trade</h2><p>Trade is the heart of commerce. Buying and selling goods and services. Both within a country (home trade) and between countries (foreign trade).</p>",
                "topics": [
                    {"title":"Home Trade (Wholesale and Retail)","order_index":1,"content":"<h3>Home Trade</h3><p><b>Retail:</b> Selling directly to final consumers. Types: Small-scale (kiosks, hawkers, street vendors, market stalls, corner shops) and Large-scale (department stores, supermarkets, chain stores, hypermarkets, mail order, online).</p><p><b>Wholesale:</b> Buying in bulk from producers, selling in smaller quantities to retailers. Functions: Storage, breaking bulk, transportation, credit, market information, price stability.</p>"},
                    {"title":"Foreign Trade","order_index":2,"content":"<h3>Foreign Trade</h3><p><b>Export:</b> Selling goods abroad. <b>Import:</b> Buying from abroad. <b>Re-export:</b> Importing then exporting.</p><p><b>Documents:</b> Bill of lading (title to goods), Invoice, Certificate of origin, Insurance certificate, Bill of exchange, Letter of credit.</p><p><b>Terms of trade:</b> FOB (Free on Board), CIF (Cost, Insurance, Freight). Balance of trade = visible exports - visible imports.</p>"}
                ]
            },
            {
                "title": "Aids to Trade",
                "slug": "aids-to-trade",
                "summary": "Advertising, insurance, banking, transportation, communication, warehousing, tourism",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Aids to Trade</h2><p>These services make trade possible. Without them, goods cannot move from producer to consumer efficiently.</p>",
                "topics": [
                    {"title":"Advertising","order_index":1,"content":"<h3>Advertising</h3><p>Any paid form of non-personal presentation of goods/services. <b>Purposes:</b> Inform, persuade, remind, create brand loyalty, increase sales.</p><p><b>Types:</b> Informative, Persuasive, Competitive. <b>Media:</b> TV, radio, newspapers, billboards, internet, social media, mobile.</p><p><b>Regulation:</b> APCON (Advertising Practitioners Council of Nigeria). Misleading/false ads prohibited.</p>"},
                    {"title":"Insurance","order_index":2,"content":"<h3>Insurance</h3><p>Protection against financial loss. <b>Principles:</b> Insurable interest, Utmost good faith, Indemnity, Subrogation, Proximate cause, Contribution.</p><p><b>Types:</b> Life (whole, term, endowment), Fire, Motor, Marine, Accident, Burglary, Agricultural.</p><p><b>NAICOM:</b> National Insurance Commission regulates. Insurance in Nigeria is compulsory for certain things (cars, buildings).</p>"},
                    {"title":"Banking and Finance","order_index":3,"content":"<h3>Banking</h3><p><b>Central Bank (CBN):</b> Controls money supply, regulates banks, monetary policy, lender of last resort.</p><p><b>Commercial banks:</b> Accept deposits, give loans, credit creation, foreign exchange, payment services, safe deposit.</p><p><b>Microfinance banks:</b> Serve low-income individuals and small businesses. <b>Merchant banks:</b> Wholesale banking, corporate finance.</p><p>Payment systems: Cheques, electronic transfer (NIP, NEFT), POS, mobile money, USSD, cards.</p>"},
                    {"title":"Transportation and Communication","order_index":4,"content":"<h3>Transportation and Communication</h3><p><b>Transport:</b> Land (road, rail), Water (inland, sea), Air, Pipeline. Each has advantages and disadvantages. Good transport reduces cost and time.</p><p><b>Communication:</b> Post, telephone, fax, internet, email, social media, video conferencing. Fast communication = efficient business.</p>"}
                ]
            },
            {
                "title": "Business Units",
                "slug": "business-units",
                "summary": "Sole proprietorship, partnership, limited liability companies, public corporations, cooperatives, mergers, privatization",
                "order_index": 4,
                "estimated_minutes": 240,
                "content": "<h2>Business Units</h2><p>Businesses come in different forms. Each has advantages and disadvantages.</p>",
                "topics": [
                    {"title":"Forms of Business Ownership","order_index":1,"content":"<h3>Business Units</h3><p><b>Sole proprietorship:</b> One owner. Simple, full control, all profit. Unlimited liability.</p><p><b>Partnership:</b> 2-20 people. Shared capital, skills, risk. Unlimited liability (except limited partners).</p><p><b>Limited liability company (Ltd):</b> Separate legal entity. Shareholders. Limited liability. Private or public.</p><p><b>Public limited company (PLC):</b> Shares sold to public. Must publish accounts. More capital. Subject to regulations.</p><p><b>Cooperative society:</b> Voluntary association for mutual benefit. Producer, consumer, thrift/credit.</p><p><b>Public corporation:</b> Government owned. Essential services (electricity, water, railways).</p>"},
                    {"title":"Entrepreneurship","order_index":2,"content":"<h3>Entrepreneurship</h3><p>Process of starting and running a business. <b>Functions:</b> Spot opportunities, raise capital, organize resources, take risks, innovate.</p><p><b>Business plan:</b> Executive summary, company description, market analysis, product/service, marketing, financial projections.</p><p><b>SMEDAN:</b> Small and Medium Enterprises Development Agency of Nigeria. Supports small businesses.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Accounting",
        "slug": "accounting",
        "category": "Business Studies",
        "icon": "file-text",
        "color": "#0891B2",
        "description": "Complete WAEC/NECO/GCE/JAMB Accounting syllabus: Principles of accounts, double entry, books of accounts, trial balance, financial statements, depreciation, company accounts, partnership, manufacturing accounts, public sector accounting",
        "lessons": [
            {
                "title": "Principles of Accounting",
                "slug": "principles-of-accounting",
                "summary": "Accounting concepts, double entry, books of original entry, ledger, trial balance, bank reconciliation",
                "order_index": 1,
                "estimated_minutes": 360,
                "content": "<h2>Principles of Accounting</h2><p>Accounting is the language of business. It records, classifies, summarizes, and interprets financial information.</p>",
                "topics": [
                    {"title":"Accounting Concepts and Conventions","order_index":1,"content":"<h3>Accounting Concepts</h3><p><b>Business entity:</b> Business separate from owner. <b>Going concern:</b> Business will continue. <b>Accrual:</b> Record when earned/incurred, not when cash received/paid.</p><p><b>Consistency:</b> Same methods each year. <b>Prudence:</b> Don't overstate assets/income. <b>Materiality:</b> Important items only.</p><p><b>Double entry:</b> Every debit has a credit. Debit = what comes in (assets, expenses). Credit = what goes out (liabilities, income, capital).</p>"},
                    {"title":"Books of Original Entry","order_index":2,"content":"<h3>Books of Original Entry</h3><p><b>Sales journal:</b> Credit sales. <b>Purchases journal:</b> Credit purchases. <b>Cash book:</b> All cash/bank transactions. <b>General journal:</b> All other entries.</p><p><b>Posting to ledger:</b> Transfer from journal to ledger accounts. Ledger has all accounts. T-accounts: Debit (left), Credit (right).</p>"},
                    {"title":"Trial Balance","order_index":3,"content":"<h3>Trial Balance</h3><p>List of all ledger balances. Debits = Credits (should balance!). If not, error exists. Errors that balance: compensating, complete reversal, omission, principle, commission.</p>"},
                    {"title":"Bank Reconciliation","order_index":4,"content":"<h3>Bank Reconciliation</h3><p>Compare cash book balance with bank statement. Differences: Unpresented cheques, uncredited deposits, bank charges, direct debits/credits, errors.</p>"}
                ]
            },
            {
                "title": "Financial Statements",
                "slug": "financial-statements",
                "summary": "Income statement, balance sheet, adjustments, depreciation, bad debts, reserves and provisions",
                "order_index": 2,
                "estimated_minutes": 300,
                "content": "<h2>Financial Statements</h2><p>Financial statements show the health of a business. The income statement shows profit. The balance sheet shows financial position.</p>",
                "topics": [
                    {"title":"Income Statement (Profit and Loss)","order_index":1,"content":"<h3>Income Statement</h3><p>Trading Account: Sales - Cost of goods sold = Gross profit. COGS = Opening stock + Purchases - Closing stock.</p><p>Profit & Loss Account: Gross profit + Other income - Expenses = Net profit.</p>"},
                    {"title":"Balance Sheet","order_index":2,"content":"<h3>Balance Sheet</h3><p>Assets = Liabilities + Capital. <b>Fixed assets:</b> Long-term (land, building, equipment). <b>Current assets:</b> Short-term (stock, debtors, cash). <b>Current liabilities:</b> Due within 1 year (creditors, bank overdraft). <b>Long-term liabilities:</b> Loans.</p>"},
                    {"title":"Depreciation","order_index":3,"content":"<h3>Depreciation</h3><p>Allocation of fixed asset cost over useful life. <b>Straight line:</b> Same amount each year. <b>Reducing balance:</b> Fixed % of net book value.</p><p>Example: N100,000 asset, 5 years life, N0 salvage. SL = N20,000/year. Reducing 20%: Y1: 20,000, Y2: 16,000, Y3: 12,800...</p>"},
                    {"title":"Adjustments","order_index":4,"content":"<h3>Year-end Adjustments</h3><p>Accruals (expenses owed but not paid), Prepayments (paid in advance), Bad debts (customers won't pay), Provision for doubtful debts (% of debtors), Depreciation.</p>"}
                ]
            },
            {
                "title": "Specialized Accounts",
                "slug": "specialized-accounts",
                "summary": "Partnership accounts, company accounts, manufacturing accounts, non-profit organizations, public sector accounting",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Specialized Accounts</h2><p>Different entities need different accounting treatments.</p>",
                "topics": [
                    {"title":"Partnership Accounts","order_index":1,"content":"<h3>Partnership</h3><p>Capital accounts, current accounts, drawings. Profit sharing: agreed ratio. Interest on capital, salary to partners.</p>"},
                    {"title":"Company Accounts","order_index":2,"content":"<h3>Limited Company</h3><p>Share capital (ordinary, preference), reserves, debentures. Published accounts: P&L, Balance Sheet, Notes. Directors' report, audit report.</p>"},
                    {"title":"Manufacturing Accounts","order_index":3,"content":"<h3>Manufacturing</h3><p>Manufacturing account shows cost of production. Prime cost (direct material + labor + expenses). Factory overhead (indirect costs). Production cost = prime cost + factory overhead + work-in-progress adjustment.</p>"},
                    {"title":"Non-Profit Organizations","order_index":4,"content":"<h3>Non-Profit Accounting</h3><p>Receipts and Payments (cash basis). Income and Expenditure (accrual basis). Subscription, donations, legacies.</p>"},
                    {"title":"Public Sector Accounting","order_index":5,"content":"<h3>Public Sector</h3><p>Government accounting. Budget (capital and recurrent). Appropriation account. Consolidated Revenue Fund. Fiscal responsibility.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Agricultural Science",
        "slug": "agricultural-science",
        "category": "Science",
        "icon": "sprout",
        "color": "#4F46E5",
        "description": "Complete WAEC/NECO/GCE/JAMB Agricultural Science syllabus: Agricultural systems, soil science, crop production, animal production, agricultural economics, farm management, agricultural extension, fisheries, forestry",
        "lessons": [
            {
                "title": "Introduction to Agriculture",
                "slug": "introduction-to-agriculture",
                "summary": "Meaning of agriculture, branches, agricultural systems, importance of agriculture to Nigerian economy",
                "order_index": 1,
                "estimated_minutes": 180,
                "content": "<h2>Introduction to Agriculture</h2><p>Agriculture is the cultivation of crops and rearing of animals. It is the backbone of Nigeria's economy, employing over 40% of the workforce.</p>",
                "topics": [
                    {"title":"What is Agriculture?","order_index":1,"content":"<h3>Agriculture Defined</h3><p>Production of plants and animals useful to humans. <b>Branches:</b> Crop production, Animal production, Fisheries, Forestry, Agricultural economics, Agricultural extension.</p><p><b>Agricultural systems:</b> Subsistence (for family), Commercial (for sale), Shifting cultivation (move when soil exhausted), Plantation (large-scale cash crops).</p><p><b>Importance:</b> Food supply, raw materials (cotton, rubber, palm oil), employment, foreign exchange, market for industrial goods.</p>"}
                ]
            },
            {
                "title": "Soil Science",
                "slug": "soil-science",
                "summary": "Soil formation, types, properties, soil fertility, soil conservation, irrigation, drainage",
                "order_index": 2,
                "estimated_minutes": 240,
                "content": "<h2>Soil Science</h2><p>Soil is the foundation of agriculture. Healthy soil = healthy crops.</p>",
                "topics": [
                    {"title":"Soil Formation and Types","order_index":1,"content":"<h3>Soil</h3><p><b>Formation:</b> Weathering of rocks (physical, chemical, biological). <b>Soil profile:</b> Horizons A (topsoil), B (subsoil), C (parent material).</p><p><b>Soil types:</b> Sandy (large particles, drains quickly, low nutrients), Clay (fine particles, holds water, high nutrients), Loam (best mix, ideal for farming).</p>"},
                    {"title":"Soil Fertility and Conservation","order_index":2,"content":"<h3>Soil Fertility</h3><p><b>Plant nutrients:</b> NPK (Nitrogen for leaves, Phosphorus for roots/fruit, Potassium for flowers/stems). Micronutrients: Mg, Ca, S, Fe, Zn, Cu.</p><p><b>Fertilizers:</b> Organic (manure, compost, green manure). Inorganic (chemical NPK, urea, superphosphate).</p><p><b>Soil conservation:</b> Crop rotation, contour plowing, terracing, cover crops, mulching, afforestation, windbreaks.</p>"}
                ]
            },
            {
                "title": "Crop Production",
                "slug": "crop-production",
                "summary": "Crop classification, crop propagation, planting, nursery, pre-planting and post-planting operations, pests and diseases, weed control, harvesting, storage",
                "order_index": 3,
                "estimated_minutes": 360,
                "content": "<h2>Crop Production</h2><p>From seed to harvest, crop production involves many operations. Each crop has specific requirements.</p>",
                "topics": [
                    {"title":"Crop Classification","order_index":1,"content":"<h3>Crop Classification</h3><p><b>By life cycle:</b> Annual (complete in 1 year -- maize, rice), Biennial (2 years -- cassava), Perennial (3+ years -- cocoa, oil palm, rubber).</p><p><b>By use:</b> Cereals (maize, rice, millet, sorghum), Legumes (beans, groundnuts, soybeans), Roots/tubers (yam, cassava, cocoyam, sweet potato), Vegetables (tomato, okra, spinach), Fruits (mango, orange, pineapple), Beverages (cocoa, coffee, tea), Oil crops (oil palm, coconut, groundnut), Fiber (cotton, jute).</p><p><b>By type:</b> Monocot (one seed leaf, parallel veins -- maize, rice) and Dicot (two seed leaves, network veins -- beans, groundnuts).</p>"},
                    {"title":"Cultivation Practices","order_index":2,"content":"<h3>Cultivation Operations</h3><p><b>Pre-planting:</b> Land clearing, plowing, harrowing, ridging. <b>Planting:</b> Seeds (maize, rice) or vegetative (yam setts, cassava stems, banana suckers). Spacing, depth, timing.</p><p><b>Post-planting:</b> Thinning, weeding, fertilizer application, irrigation, pest/disease control, staking (yam).</p><p><b>Harvesting:</b> Time varies by crop. Signs: yellow leaves, dry pods, etc. Methods: manual or mechanical.</p>"},
                    {"title":"Pests and Diseases","order_index":3,"content":"<h3>Crop Pests and Diseases</h3><p><b>Common pests:</b> Stem borers (maize), grasshoppers, aphids, weevils (storage), rodents, birds. Control: Cultural (crop rotation), Biological (natural predators), Chemical (pesticides), Integrated (IPM).</p><p><b>Diseases:</b> Fungal (rust, smut, blight), Bacterial (wilt, rot), Viral (mosaic, leaf curl). Control: Resistant varieties, fungicides, crop rotation, sanitation.</p>"}
                ]
            },
            {
                "title": "Animal Production",
                "slug": "animal-production",
                "summary": "Types of farm animals, animal reproduction, breeds, nutrition, feeds, animal health, disease control, animal husbandry",
                "order_index": 4,
                "estimated_minutes": 300,
                "content": "<h2>Animal Production</h2><p>Farm animals provide meat, milk, eggs, hides, and more. Good management = healthy, productive animals.</p>",
                "topics": [
                    {"title":"Types of Farm Animals","order_index":1,"content":"<h3>Farm Animals</h3><p><b>Ruminants:</b> Cattle, sheep, goats -- multi-chambered stomach (rumen), chew cud. <b>Non-ruminants:</b> Pigs, poultry, rabbits -- simple stomach.</p><p><b>Breeds:</b> Beef cattle (White Fulani, Ndama). Dairy (Friesian, Jersey). Sheep (West African Dwarf, Merino). Goats (West African Dwarf, Sokoto Red). Pigs (Large White, Landrace). Poultry (Broilers, Layers).</p>"},
                    {"title":"Animal Reproduction","order_index":2,"content":"<h3>Reproduction</h3><p>Mating systems: natural (pasture mating, hand mating) and artificial insemination. Gestation periods: Cattle 283 days, Sheep 150, Goats 150, Pigs 114, Rabbits 31.</p>"},
                    {"title":"Animal Nutrition","order_index":3,"content":"<h3>Feeds and Nutrition</h3><p><b>Feed components:</b> Carbohydrates (energy), Proteins (growth), Fats (energy), Minerals, Vitamins, Water.</p><p><b>Concentrates:</b> High energy/nutrient (maize, groundnut cake, fishmeal). <b>Roughage:</b> High fiber (hay, silage, pasture grass).</p><p><b>Ruminant digestion:</b> Rumen -> Reticulum -> Omasum -> Abomasum (true stomach). Microorganisms digest cellulose.</p>"},
                    {"title":"Animal Diseases","order_index":4,"content":"<h3>Animal Diseases</h3><p><b>Bacterial:</b> Anthrax (cattle, sheep, goats), Brucellosis (contagious abortion), Tuberculosis, Mastitis.</p><p><b>Viral:</b> Newcastle disease (poultry), Rinderpest (cattle -- now eradicated!), Foot and mouth disease, Rabies.</p><p><b>Protozoan:</b> Trypanosomiasis (sleeping sickness, tsetse fly), Coccidiosis.</p><p><b>Parasitic:</b> Internal (roundworms, tapeworms, liver fluke), External (ticks, lice, mites, fleas).</p><p><b>Control:</b> Vaccination, quarantine, good hygiene, proper nutrition, veterinary care, dipping/spraying.</p>"}
                ]
            },
            {
                "title": "Agricultural Economics and Extension",
                "slug": "agricultural-economics-and-extension",
                "summary": "Farm management, farm records, production function, marketing, agricultural extension, finance, agricultural policies",
                "order_index": 5,
                "estimated_minutes": 240,
                "content": "<h2>Agricultural Economics and Extension</h2><p>Farming is a business. Economics helps farmers make better decisions. Extension helps them learn new techniques.</p>",
                "topics": [
                    {"title":"Farm Management","order_index":1,"content":"<h3>Farm Management</h3><p><b>Factors of production:</b> Land, labor, capital, management. <b>Farm records:</b> Inventory, production, financial, labor records.</p><p><b>Cost concepts:</b> Fixed costs (rent, equipment), Variable costs (seeds, fertilizer, labor). Total cost = FC+VC.</p><p><b>Revenue:</b> Income from sales. Profit = Revenue - Total cost.</p>"},
                    {"title":"Agricultural Marketing","order_index":2,"content":"<h3>Marketing</h3><p>Moving farm products from producer to consumer. Problems: Perishability, poor transport, lack of storage, price fluctuations, middlemen exploitation. Solutions: Storage facilities, good roads, market information, cooperatives.</p>"},
                    {"title":"Agricultural Extension","order_index":3,"content":"<h3>Extension Services</h3><p>Teaching farmers better methods. Methods: Demonstration (result and method), farm visits, meetings, radio/TV, leaflets. ADP (Agricultural Development Programme) in each state.</p>"}
                ]
            }
        ]
    },
    {
        "name": "Further Mathematics",
        "slug": "further-mathematics",
        "category": "Science",
        "icon": "sigma",
        "color": "#1D4ED8",
        "description": "Complete WAEC/NECO/GCE/JAMB Further Mathematics syllabus: Advanced algebra, calculus (differentiation and integration), vectors and mechanics, coordinate geometry, complex numbers, matrices, statistics, probability distributions",
        "lessons": [
            {
                "title": "Advanced Algebra",
                "slug": "advanced-algebra",
                "summary": "Quadratic functions, polynomials, partial fractions, inequalities, matrices, determinants, series, mathematical induction, binomial theorem",
                "order_index": 1,
                "estimated_minutes": 300,
                "content": "<h2>Advanced Algebra</h2><p>Further Math algebra extends the concepts from ordinary mathematics. Quadratic theory, polynomial division, partial fractions, and more.</p>",
                "topics": [
                    {"title":"Quadratic Functions and Theory","order_index":1,"content":"<h3>Quadratic Functions</h3><p>ax^2+bx+c. Discriminant D=b^2-4ac. Nature of roots: D>0 (real, distinct), D=0 (real, equal), D<0 (complex).</p><p>Sum of roots = -b/a. Product = c/a. Form equation: x^2 - (sum)x + product = 0. Max/min: vertex at -b/2a.</p>"},
                    {"title":"Polynomials and Remainder Theorem","order_index":2,"content":"<h3>Polynomials</h3><p>Degree n: a_n x^n + ... + a_1 x + a_0. <b>Remainder theorem:</b> P(x)/(x-a) -> remainder = P(a). <b>Factor theorem:</b> If P(a)=0, (x-a) is factor.</p><p><b>Synthetic division:</b> Quick method to divide polynomials.</p>"},
                    {"title":"Partial Fractions","order_index":3,"content":"<h3>Partial Fractions</h3><p>Express a complex fraction as sum of simpler fractions. Types: (1) Distinct linear factors, (2) Repeated linear factors, (3) Quadratic factors.</p><p>Example: (5x+3)/(x^2-4) = A/(x-2) + B/(x+2). Multiply: 5x+3 = A(x+2)+B(x-2). Solve: A=13/4, B=7/4.</p>"}
                ]
            },
            {
                "title": "Calculus",
                "slug": "calculus",
                "summary": "Differentiation, techniques of differentiation, applications of differentiation, integration, techniques of integration, applications of integration",
                "order_index": 2,
                "estimated_minutes": 360,
                "content": "<h2>Calculus</h2><p>Calculus is the mathematics of change and accumulation. Further Math calculus is deeper and more applied.</p>",
                "topics": [
                    {"title":"Differentiation","order_index":1,"content":"<h3>Differentiation Techniques</h3><p>y=x^n -> dy/dx=nx^(n-1). Product rule: d(uv)/dx = u dv/dx + v du/dx. Quotient rule: d(u/v)/dx = (v du/dx - u dv/dx)/v^2.</p><p>Chain rule: dy/dx = dy/du x du/dx. Second derivative: d^2y/dx^2 = differentiate again.</p>"},
                    {"title":"Applications of Differentiation","order_index":2,"content":"<h3>Applications</h3><p><b>Stationary points:</b> Set dy/dx=0. Second derivative test: >0 min, <0 max, =0 could be point of inflection.</p><p><b>Rates of change:</b> Related rates. dV/dt = dV/dr x dr/dt. <b>Small changes:</b> delta_y approx dy/dx x delta_x.</p>"},
                    {"title":"Integration","order_index":3,"content":"<h3>Integration Techniques</h3><p>Integral x^n dx = x^(n+1)/(n+1) + C (n not -1). Integral 1/x dx = ln|x| + C. Integral e^x dx = e^x + C.</p><p><b>By substitution:</b> Let u = g(x), du = g'(x)dx. <b>By parts:</b> Integral u dv = uv - Integral v du.</p><p><b>Definite integrals:</b> Integral_a^b f(x)dx = F(b)-F(a). Area between curves, volume of revolution.</p>"}
                ]
            },
            {
                "title": "Vectors and Mechanics",
                "slug": "vectors-and-mechanics",
                "summary": "Vector algebra, dot product, cross product, kinematics, projectiles, statics, dynamics, equilibrium, friction",
                "order_index": 3,
                "estimated_minutes": 300,
                "content": "<h2>Vectors and Mechanics</h2><p>Vectors describe quantities with direction. Mechanics applies math to physical systems.</p>",
                "topics": [
                    {"title":"Vector Algebra","order_index":1,"content":"<h3>Vectors</h3><p>a = (x,y,z). Addition, scalar multiplication. Dot product: a.b = |a||b|cos(theta) = x1x2+y1y2+z1z2. Cross product: axb = |a||b|sin(theta) n. Perpendicular if a.b=0. Parallel if axb=0.</p>"},
                    {"title":"Kinematics","order_index":2,"content":"<h3>Kinematics</h3><p>v=u+at, s=ut+0.5at^2, v^2=u^2+2as. Displacement, velocity, acceleration vectors. Projectile motion with vectors: R(t) = (u cos theta)t i + (u sin theta t - 0.5gt^2) j.</p>"},
                    {"title":"Statics and Dynamics","order_index":3,"content":"<h3>Statics and Dynamics</h3><p>Equilibrium: Sum of forces = 0, sum of moments = 0. Friction: F = mu R. Dynamics: F=ma. Momentum, impulse, work, energy. Conservation of mechanical energy.</p>"}
                ]
            },
            {
                "title": "Coordinate Geometry and Complex Numbers",
                "slug": "coordinate-geometry-and-complex-numbers",
                "summary": "Straight lines, circles, parabola, ellipse, hyperbola, complex numbers, De Moivre's theorem, argand diagram",
                "order_index": 4,
                "estimated_minutes": 240,
                "content": "<h2>Coordinate Geometry and Complex Numbers</h2><p>Geometry meets algebra. Complex numbers extend the number system to include imaginary numbers.</p>",
                "topics": [
                    {"title":"Coordinate Geometry","order_index":1,"content":"<h3>Conic Sections</h3><p><b>Circle:</b> (x-h)^2+(y-k)^2=r^2. <b>Parabola:</b> y^2=4ax or x^2=4ay. Focus-directrix property.</p><p><b>Ellipse:</b> x^2/a^2+y^2/b^2=1. <b>Hyperbola:</b> x^2/a^2-y^2/b^2=1.</p><p><b>Transformation:</b> Translation, reflection, rotation, enlargement. Matrix representation.</p>"},
                    {"title":"Complex Numbers","order_index":2,"content":"<h3>Complex Numbers</h3><p>z = x + iy where i^2=-1. Argand diagram: x axis real, y axis imaginary. Modulus: |z| = sqrt(x^2+y^2). Argument: arg z = tan^-1(y/x).</p><p>Polar form: z = r(cos theta + i sin theta) = r cis theta. De Moivre: (cos theta+i sin theta)^n = cos n theta+i sin n theta.</p>"}
                ]
            }
        ]
    }
]
