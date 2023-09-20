from main import ProducedNewsArticle


urls = [
    "https://thehill.com/opinion/international/4210108-biden-addresses-a-world-skeptical-of-yet-desperately-needing-us-leadership/",
    "https://abcnews.go.com/Politics/speaker-mccarthy-plans-confront-zelenskyy-ukraine-funding/story?id=103313355"
]

test_article = ProducedNewsArticle(
        title='Test title!',
        content=[
            ProducedNewsArticle.ProducedParagraph(
                text="President Joe Biden is preparing to address an international audience at the United Nations amidst uncertainties in the global political arena, like the largest war in Europe since World War II and China's rising influence. The address comes at a time when the world is both skeptical of and desperate for American leadership. As the relative decline of American economic and military power creates a vacuum in global order, countries are vying for dominance while the nature of relationships at global and regional levels evolves in this era of great power competition.",
                sources=[
                    ProducedNewsArticle.ProducedParagraph.Source(
                        article_index=0,
                        article_texts=[
                            "President Joe Biden is preparing to address an international audience at the United Nations amidst uncertainties in the global political arena, like the largest war in Europe since World War II and China's rising influence. The address comes at a time when the world is both skeptical of and desperate for American leadership. As the relative decline of American economic and military power creates a vacuum in global order, countries are vying for dominance while the nature of relationships at global and regional levels evolves in this era of great power competition."
                        ],
                        reason="The reason is to provide context for the article."
                    )
                ]
            ),
            ProducedNewsArticle.ProducedParagraph(
                text="Representative Kevin McCarthy, House Speaker, has shared his reservations about the aid to Ukraine, a topic that has caused intraparty strife within the Congress. The controversy surrounding Ukraine funding will take center stage when Ukrainian President Volodymyr Zelenskyy meets with lawmakers in Washington. While the White House and some Republicans support an additional $24 billion in support of Ukraine, skeptical Republicans demand accountability for the aid money.",
                sources=[
                    ProducedNewsArticle.ProducedParagraph.Source(
                        article_index=1,
                        article_texts=[
                            "Representative Kevin McCarthy, House Speaker, has shared his reservations about the aid to Ukraine, a topic that has caused intraparty strife within the Congress. The controversy surrounding Ukraine funding will take center stage when Ukrainian President Volodymyr Zelenskyy meets with lawmakers in Washington. While the White House and some Republicans support an additional $24 billion in support of Ukraine, skeptical Republicans demand accountability for the aid money."
                        ],
                        reason="The reason is to provide context for the article."
                    ),
                    ProducedNewsArticle.ProducedParagraph.Source(
                        article_index=0,
                        article_texts=[
                            "President Joe Biden is preparing to address an international audience at the United Nations amidst uncertainties in the global political arena, like the largest war in Europe since World War II and China's rising influence. The address comes at a time when the world is both skeptical of and desperate for American leadership. As the relative decline of American economic and military power creates a vacuum in global order, countries are vying for dominance while the nature of relationships at global and regional levels evolves in this era of great power competition."
                        ],
                        reason="The reason is to provide context for the article."
                    )
                ]
            ),
            ProducedNewsArticle.ProducedParagraph(
                text="Biden's agenda, along with issues such as Ukraine's assistance, are of importance at a time when alliances are shifting and power balances are being challenged on the global stage. Both leaders, Biden and Zelenskyy are set to meet, a move that will certainly influence these critical discussions.",
                sources=[
                    ProducedNewsArticle.ProducedParagraph.Source(
                        article_index=1,
                        article_texts=[
                            "Biden's agenda, along with issues such as Ukraine's assistance, are of importance at a time when alliances are shifting and power balances are being challenged on the global stage. Both leaders, Biden and Zelenskyy are set to meet, a move that will certainly influence these critical discussions."
                        ],
                        reason="The reason is to provide context for the article."
                    ),
                    ProducedNewsArticle.ProducedParagraph.Source(
                        article_index=0,
                        article_texts=[
                            "President Joe Biden is preparing to address an international audience at the United Nations amidst uncertainties in the global political arena, like the largest war in Europe since World War II and China's rising influence. The address comes at a time when the world is both skeptical of and desperate for American leadership. As the relative decline of American economic and military power creates a vacuum in global order, countries are vying for dominance while the nature of relationships at global and regional levels evolves in this era of great power competition."
                        ],
                        reason="The reason is to provide context for the article."
                    )
                ]
            )
        ]
    )