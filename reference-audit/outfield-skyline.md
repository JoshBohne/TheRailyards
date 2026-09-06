# Outfield skyline reference audit

This is a scoped skyline pass for the September 2026 west-bank Railyards concept. It identifies real Chicago buildings that could appear beyond the proposed outfield from the supplied interior cameras. The AECOM images show illustrative future development around the site; those proposed masses are intentionally excluded here so the list stays useful for recognizable real-world silhouettes.

The shared model frame places home plate at local `[0, 0]`, with X east and Y north. First base is +X, third base is +Y, and the traced center-field direction is about local azimuth 52.6 degrees. The two supplied home-oriented cameras are centered near 45.0 degrees (field eye) and 46.3 degrees (home upper deck). Their horizontal fields of view are approximately 78.6 and 71.5 degrees, so both include the east-northeast cluster from St. Regis through Trump/875, but they do not include Willis Tower, which is almost due north at local azimuth 89.3 degrees.

## Credible default cluster

The first skyline layer should be the compact east-northeast group: The St. Regis Chicago, Aqua, Aon Center, Two Prudential Plaza, and Trump International Hotel & Tower. They fall 5.5 to 20.8 degrees left of the center-field direction and are inside both home-camera frustums. From the upper deck their crowns should read above the 46–48 m canopy; from the field-eye camera the bowl roof, outfield screens, and proposed buildings will hide much of each lower mass. Model crowns and upper silhouettes before attempting street-level context.

Two Prudential Plaza and One Prudential Plaza should be treated as a pair. The taller Two Pru provides the strong stepped crown; One Pru is a shorter supporting block at almost the same azimuth. The St. Regis supplies the most distinctive form: three offset, stacked frustum stems rather than a generic glass box. Aqua supplies the irregular horizontal balcony waves. Aon is the quiet white monolith. Trump supplies a tapered dark tower and narrow spire.

875 North Michigan Avenue (the former John Hancock Center) remains plausible at the edge of both home views because its 73-degree local azimuth is near Trump. Its X-bracing and antenna masts are more useful than its width at nearly 4 km. Tribune Tower, Wrigley Building, and Marina City are optional historic accents: they are inside the frustums, but their lower heights mean they will usually be hidden behind taller towers or the bowl. Marina City’s twin cylindrical “corn cobs” are the strongest of those accents.

## Willis/Sears Tower finding

Willis Tower is real, very tall, and close, but it should not be assumed visible in the default home-plate composition. Its registered center is approximately local `[19, 1574]` m, local azimuth 89.3 degrees, almost directly along the left-field foul direction. That places it roughly 36–37 degrees left of the traced center-field heading and outside both supplied horizontal frustums. A wider or deliberately panned left-field camera could show its black stepped bundled-tube crown and antennae. For the supplied home views, leave it disabled or mark it as a conditional left-field landmark; a partial tip appearing through an opening would require a dedicated geometry/line-of-sight check.

The apparent contradiction between “nearby and tall” and “not visible” is purely bearing and framing: the stadium’s outfield sightline points northeast while Willis is nearly due north. The model’s documented +33 m X registration adjustment and approximately 4–5 m site-plan residual do not materially change that 36-degree angular separation.

## Wider left-field candidates

Salesforce Tower Chicago, River Point, and 150 North Riverside are real towers west/northwest of the site, but their local azimuths are 92.8, 96.4, and 94.7 degrees. They are outside the supplied home and upper-deck frustums and should be reserved for a panned left-field or bridge view. Their inclusion in a default center-field skyline would be a framing error even though they are geographically close.

## Source and modeling boundaries

Coordinates are OSM building centers/footprints retrieved through the public [Overpass API](https://overpass-api.de/api/interpreter), with [ODbL attribution](https://www.openstreetmap.org/copyright). The local XY conversion uses the shared scene reference at 41.8645, -87.6362, the recorded home offset, and the documented inferred +33 m X alignment. It is appropriate for silhouette placement and azimuth ranking, not survey control.

Heights use the building owner/developer/architect where available, supplemented by the [Council on Tall Buildings and Urban Habitat / Skyscraper Center Chicago list](https://www.skyscrapercenter.com/city/chicago). The JSON keeps architectural and tip heights separate for towers with antennas or spires. Tribune Tower and Wrigley Building are deliberately approximate low-rise silhouette heights because the available OSM records provide footprint/levels rather than a clean authoritative architectural height; they should remain low-priority accents.

The full per-building coordinates, azimuths, distances, camera frustum membership, expected occlusion, source URLs, and silhouette specifications are in [skyline-buildings.json](skyline-buildings.json).

### Source links used for the defining towers

- [Willis Tower official history and height](https://www.willistower.com/news/iconic-willis-tower-becomes-largest-building-in-the-u-s-to-earn-leed) and [CTBUH profile](https://www.skyscrapercenter.com/building/willis-tower/169)
- [Aon Center official facts](https://www.aoncenter.info/pdf/Aon%20center%20fun%20facts%20%288%29.pdf) and [CTBUH profile](https://www.skyscrapercenter.com/building/aon-center/339)
- [The St. Regis / Vista Tower by Studio Gang](https://studiogang.com/projects/vista-tower/) and [CTBUH profile](https://www.skyscrapercenter.com/building/the-st-regis-chicago/17137)
- [Aqua by Magellan Development](https://www.magellandevelopment.com/projects/aqua/) and [CTBUH profile](https://www.skyscrapercenter.com/building/aqua/886)
- [875 North Michigan CTBUH profile](https://www.skyscrapercenter.com/building/875-north-michigan-avenue/345)
- [Two Prudential Plaza CTBUH profile](https://www.skyscrapercenter.com/building/two-prudential-plaza/489)
- [Trump International Hotel & Tower CTBUH profile](https://www.skyscrapercenter.com/building/wd/203)
- [Salesforce Tower Chicago official media](https://www.salesforce.com/news/media-collection/salesforce-tower-chicago/)
- [River Point official site](https://chicagoriverpoint.com/)
- [150 North Riverside project data](https://www.gpchicago.com/architecture/150-north-riverside/)
