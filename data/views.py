from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, FriendRequest, Post, PostLike, Notification
from .serializers import *
from .permissions import IsOwnerOrReadOnly
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404



class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserProfilePictureView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.profile_picture_blob:
            return HttpResponse(user.profile_picture_blob, content_type="image/png")
        raise Http404

class UserHeaderPictureView(APIView):
    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user.header_picture_blob:
            return HttpResponse(user.header_picture_blob, content_type="image/png")
        raise Http404


class RegisterView(APIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully"}, status=201)
        return Response(serializer.errors, status=400)

class FriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List all friend requests involving the current user"""
        friend_requests = FriendRequest.objects.filter(
            Q(from_user=request.user) | Q(to_user=request.user)
        )
        serializer = FriendRequestSerializer(friend_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Send a friend request to another user"""
        to_user_id = request.data.get('to_user_id')
        if not to_user_id:
            return Response({'error': 'to_user_id is required'}, status=400)

        if request.user.id == int(to_user_id):
            return Response({'error': 'You cannot friend yourself'}, status=400)

        to_user = User.objects.filter(id=to_user_id).first()
        if not to_user:
            return Response({'error': 'User not found'}, status=404)

        # Check for an existing request in either direction
        existing_request = FriendRequest.objects.filter(
            Q(from_user=request.user, to_user=to_user) |
            Q(from_user=to_user, to_user=request.user)
        ).first()

        if existing_request:
            if existing_request.status == 'accepted':
                return Response({'error': 'You are already friends with this user.'}, status=409)
            elif existing_request.status == 'pending':
                return Response({'error': 'A friend request is already pending between you two.'}, status=409)
            elif existing_request.status == 'rejected':
                # Update the existing request to reflect the new sender and reset status
                existing_request.from_user = request.user
                existing_request.to_user = to_user
                existing_request.status = 'pending'
                existing_request.save()
                return Response(FriendRequestSerializer(existing_request).data, status=200)

        # No existing request at all — create a new one
        friend_request = FriendRequest.objects.create(
            from_user=request.user,
            to_user=to_user,
            status='pending'
        )
        serializer = FriendRequestSerializer(friend_request)
        return Response(serializer.data, status=201)

    # def patch(self, request, pk):
    #     """Respond to a friend request (accept/reject)"""
    #     friend_request = FriendRequest.objects.filter(id=pk, to_user=request.user).first()
    #     if not friend_request:
    #         return Response({'error': 'Friend request not found or you are not authorized to respond.'}, status=status.HTTP_404_NOT_FOUND)

    #     status_value = request.data.get('status')
    #     if status_value not in ['accepted', 'rejected']:
    #         return Response({'error': 'Invalid status. Must be "accepted" or "rejected".'}, status=status.HTTP_400_BAD_REQUEST)

    #     friend_request.status = status_value
    #     friend_request.save()

    #     if status_value == 'accepted':
    #         # Optionally, you can create a notification or update friend counts here
    #         pass

    #     return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)
    

    def patch(self, request, pk):
        """Respond to a friend request (accept/reject or cancel if sender)"""
        friend_request = FriendRequest.objects.filter(id=pk).first()
        if not friend_request:
            return Response({'error': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

        status_value = request.data.get('status')
        if status_value not in ['accepted', 'rejected']:
            return Response({'error': 'Invalid status. Must be "accepted" or "rejected".'}, status=status.HTTP_400_BAD_REQUEST)

        # Accept/reject logic for recipient
        if friend_request.to_user == request.user:
            friend_request.status = status_value
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)

        # Allow sender to cancel (rejected) only if still pending
        if friend_request.from_user == request.user and friend_request.status == 'pending' and status_value == 'rejected':
            friend_request.status = 'rejected'
            friend_request.save()
            return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_200_OK)

        return Response({'error': 'You are not authorized to update this request.'}, status=status.HTTP_403_FORBIDDEN)


    def delete(self, request, pk):
        """Unfriend a user (set the status to 'rejected')"""
        friend_request = FriendRequest.objects.filter(
            id=pk,
            status='accepted'
        ).filter(
            Q(from_user=request.user) | Q(to_user=request.user)
        ).first()

        if not friend_request:
            return Response({'error': 'Friendship not found or not authorized.'}, status=404)

        friend_request.status = 'rejected'
        friend_request.save()
        return Response({'message': 'Unfriended successfully.'}, status=200)


class FriendsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """List all accepted friends of the current user"""
        accepted_requests = FriendRequest.objects.filter(
            status='accepted'
        ).filter(
            Q(from_user=request.user) | Q(to_user=request.user)
        )
        friends = []
        for fr in accepted_requests:
            if fr.from_user == request.user:
                friends.append(fr.to_user)
            else:
                friends.append(fr.from_user)

        serializer = UserSerializer(friends, many=True)
        return Response(serializer.data)


class PostListCreateView(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)



class LikePostView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if not post:
            return Response({'error': 'Post not found'}, status=404)
        like, created = PostLike.objects.get_or_create(post=post, user=request.user)
        if not created:
            return Response({'message': 'Already liked'}, status=200)
        if post.author != request.user:
            Notification.objects.create(
                user=post.author,  # recipient
                from_user=request.user,  # sender
                message=f"@{request.user.username} liked your post.",
                type='like'
            )
        return Response({'message': 'Post liked'}, status=201)
    def delete(self, request, post_id):
        post = Post.objects.filter(id=post_id).first()
        if not post:
            return Response({'error': 'Post not found'}, status=404)
        like = PostLike.objects.filter(post=post, user=request.user).first()
        if not like:
            return Response({'error': 'You have not liked this post'}, status=400)
        like.delete()
        return Response({'message': 'Post unliked'}, status=204)

# class LikePostView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def post(self, request, post_id):
#         post = Post.objects.filter(id=post_id).first()
#         if not post:
#             return Response({'error': 'Post not found'}, status=404)

#         like = PostLike.objects.filter(post=post, user=request.user).first()
#         if like:
#             # User already liked it — remove like (toggle off)
#             like.delete()
#             return Response({'message': 'Post unliked'}, status=200)

#         # Not liked yet — add like (toggle on)
#         PostLike.objects.create(post=post, user=request.user)

#         if post.author != request.user:
#             Notification.objects.create(
#                 user=post.author,
#                 from_user=request.user,
#                 message=f"@{request.user.username} liked your post.",
#                 type='like'
#             )

#         return Response({'message': 'Post liked'}, status=201)



class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def patch(self, request, pk=None):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = NotificationSerializer(notification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk=None):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

        notification.delete()
        return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

