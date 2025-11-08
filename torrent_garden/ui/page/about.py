import reflex as rx

from torrent_garden.ui.page.base import page_base


def page_about() -> rx.Component:
    return page_base(
        rx.container(
            rx.vstack(
                rx.heading("About", size="8", mb="4"),
                rx.vstack(
                    rx.text(
                        "Welcome to Torrent Garden - a completely automated torrent indexing platform.",
                        size="5",
                        mb="3"
                    ),
                    rx.text(
                        "This website operates entirely through automated crawlers that continuously monitor "
                        "and listen to the Distributed Hash Table (DHT) network. Our crawlers passively collect "
                        "torrent metadata that is already publicly available on the DHT network and automatically "
                        "populate our database with this information.",
                        size="3",
                        mb="3"
                    ),
                    rx.text(
                        "Important: No human moderation or censorship takes place on this platform. All content "
                        "is automatically indexed from the DHT network without any editorial oversight, content "
                        "filtering, or manual intervention. We do not review, approve, or remove torrents based "
                        "on their content.",
                        size="3",
                        mb="3",
                        weight="medium"
                    ),
                    rx.text(
                        "The DHT network is a decentralized system where torrent information is shared peer-to-peer. "
                        "Our crawlers simply observe and record this publicly available data. We act as a search "
                        "engine for torrents that already exist in the distributed network, making them easier to "
                        "discover and access.",
                        size="3",
                        mb="3"
                    ),
                    rx.text(
                        "Since our platform is fully automated and relies on DHT network data, the availability "
                        "and accuracy of torrent information depends entirely on what is being shared across the "
                        "network by peers worldwide. We cannot guarantee the quality, legality, or safety of any "
                        "torrents indexed by our system.",
                        size="3",
                        mb="3"
                    ),
                    rx.text(
                        "Users should exercise caution and comply with their local laws when accessing any torrented "
                        "content. This platform serves purely as an indexing service for publicly available DHT data.",
                        size="3",
                        style={"font-style": "italic"}
                    ),
                    spacing="4",
                    align="start",
                    max_width="800px"
                ),
                spacing="6",
                align="center",
                padding="6"
            ),
            width="100%",
        )
    )


@rx.page("/about", title="About")
def about() -> rx.Component:
    return page_about()
