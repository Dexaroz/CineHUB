from typing import Optional, List

from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError

from app.domain.entities.movie import Movie
from app.domain.repositories.movie_repository import MovieRepository
from app.domain.vo.rating import Rating


class DynamoDBMovieRepository(MovieRepository):
    def __init__(self, table):
        self.table = table

    def add(self, movie: Movie) -> None:
        item = {
            'id': movie.id,
            'title': movie.title,
            'genre': movie.genre,
            'director': movie.director,
            'year': movie.year,
            'rate': movie.rate.value,
            'poster': movie.poster,
            'synopsis': movie.synopsis,
            'duration': movie.duration,
        }
        try:
            self.table.put_item(Item=item)
        except ClientError as e:
            raise RuntimeError(f"Error adding movie to DynamoDB: {e}")

    def get(self, movie_id: int) -> Optional[Movie]:
        try:
            response = self.table.get_item(Key={'id': movie_id})
            item = response.get('Item')
            if not item:
                return None
            return self._item_to_movie(item)
        except ClientError as e:
            raise RuntimeError(f"Error getting movie from DynamoDB: {e}")

    def remove(self, movie_id: int) -> bool:
        try:
            response = self.table.delete_item(
                Key={'id': movie_id},
                ReturnValues='ALL_OLD'
            )
            return 'Attributes' in response
        except ClientError as e:
            raise RuntimeError(f"Error deleting movie from DynamoDB: {e}")

    def list(
            self,
            *,
            genre: str | None = None,
            director: str | None = None,
            search: str | None = None,
    ) -> List[Movie]:
        try:
            if genre or director or search:
                return self._filtered_scan(genre, director, search)

            response = self.table.scan()
            items = response.get('Items', [])

            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                items.extend(response.get('Items', []))

            return [self._item_to_movie(item) for item in items]
        except ClientError as e:
            raise RuntimeError(f"Error listing movies from DynamoDB: {e}")

    def _filtered_scan(
            self,
            genre: str | None,
            director: str | None,
            search: str | None
    ) -> List[Movie]:
        filter_expression = None

        if genre:
            filter_expression = Attr('genre').eq(genre)

        if director:
            director_filter = Attr('director').eq(director)
            filter_expression = director_filter if not filter_expression else filter_expression & director_filter

        if search:
            search_filter = Attr('title').contains(search) | Attr('synopsis').contains(search)
            filter_expression = search_filter if not filter_expression else filter_expression & search_filter

        if filter_expression:
            response = self.table.scan(FilterExpression=filter_expression)
        else:
            response = self.table.scan()

        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            if filter_expression:
                response = self.table.scan(
                    FilterExpression=filter_expression,
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
            else:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        return [self._item_to_movie(item) for item in items]

    @staticmethod
    def _item_to_movie(item: dict) -> Movie:
        return Movie(
            id=int(item['id']),
            title=item['title'],
            genre=item['genre'],
            director=item['director'],
            year=int(item['year']),
            rate=Rating(int(item['rate'])),
            poster=item['poster'],
            synopsis=item['synopsis'],
            duration=int(item['duration']),
        )

    def get_max_id(self) -> int:
        try:
            response = self.table.scan(
                ProjectionExpression='id'
            )
            items = response.get('Items', [])

            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ProjectionExpression='id',
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
                items.extend(response.get('Items', []))

            if not items:
                return 0

            return max(int(item['id']) for item in items)
        except ClientError as e:
            raise RuntimeError(f"Error getting max ID from DynamoDB: {e}")