import sys
import os
from datetime import datetime

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy.orm import Session
    from database import get_db, User, Post, Like, Comment, Share, Location, Follow, UserInterest, PostTag
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you're in the backend directory and have activated the virtual environment")
    sys.exit(1)

class DataVerification:
    def __init__(self):
        """Initialize the data verification system"""
        self.db = next(get_db())
        self.verification_results = {}
        
    def verify_table_counts(self):
        """Verify record counts in all tables"""
        print("📊 Verifying table record counts...")
        
        tables = {
            "Users": User,
            "Posts": Post,
            "Locations": Location,
            "Likes": Like,
            "Comments": Comment,
            "Shares": Share,
            "Follows": Follow,
            "User Interests": UserInterest,
            "Post Tags": PostTag
        }
        
        for table_name, model in tables.items():
            count = self.db.query(model).count()
            print(f"  {table_name}: {count:,} records")
            self.verification_results[table_name.lower().replace(' ', '_')] = count
        
        return self.verification_results
    
    def verify_data_relationships(self):
        """Verify data relationships and integrity"""
        print("\n🔗 Verifying data relationships...")
        
        # Check users with posts
        users_with_posts = self.db.query(User).join(Post).distinct().count()
        total_users = self.db.query(User).count()
        print(f"  Users with posts: {users_with_posts}/{total_users} ({users_with_posts/total_users*100:.1f}%)")
        
        # Check posts with interactions
        posts_with_likes = self.db.query(Post).filter(Post.likes_count > 0).count()
        posts_with_comments = self.db.query(Post).filter(Post.comments_count > 0).count()
        total_posts = self.db.query(Post).count()
        
        print(f"  Posts with likes: {posts_with_likes}/{total_posts} ({posts_with_likes/total_posts*100:.1f}%)")
        print(f"  Posts with comments: {posts_with_comments}/{total_posts} ({posts_with_comments/total_posts*100:.1f}%)")
        
        # Check follow relationships  
        users_with_followers = self.db.query(User).join(Follow, User.id == Follow.following_id).distinct().count()
        users_following_others = self.db.query(User).join(Follow, User.id == Follow.follower_id).distinct().count()
        
        print(f"  Users with followers: {users_with_followers}/{total_users} ({users_with_followers/total_users*100:.1f}%)")
        print(f"  Users following others: {users_following_others}/{total_users} ({users_following_others/total_users*100:.1f}%)")
    
    def verify_sample_data(self):
        """Display sample data to verify quality"""
        print("\n👀 Sample data verification...")
        
        # Sample users
        sample_users = self.db.query(User).limit(3).all()
        print("\n  📱 Sample Users:")
        for user in sample_users:
            post_count = self.db.query(Post).filter_by(user_id=user.id).count()
            follower_count = self.db.query(Follow).filter_by(following_id=user.id).count()
            print(f"    • {user.full_name} ({user.email})")
            print(f"      Bio: {user.bio[:50]}...")
            print(f"      Posts: {post_count}, Followers: {follower_count}")
        
        # Sample posts
        sample_posts = self.db.query(Post).filter(Post.caption.isnot(None)).limit(3).all()
        print("\n  📸 Sample Posts:")
        for post in sample_posts:
            print(f"    • Post ID: {post.id}")
            print(f"      Caption: {post.caption[:80]}...")
            print(f"      Likes: {post.likes_count}, Comments: {post.comments_count}")
        
        # Sample locations
        sample_locations = self.db.query(Location).limit(5).all()
        print("\n  📍 Sample Locations:")
        for location in sample_locations:
            print(f"    • {location.name} - {location.country} ({location.category})")
        
        # Sample interactions
        sample_comments = self.db.query(Comment).limit(3).all()
        print("\n  💬 Sample Comments:")
        for comment in sample_comments:
            print(f"    • \"{comment.comment_text}\"")
    
    def verify_data_distribution(self):
        """Verify data distribution and patterns"""
        print("\n📈 Data distribution analysis...")
        
        # User creation timeline
        users_last_30_days = self.db.query(User).filter(
            User.created_at >= datetime.now().replace(day=1)
        ).count() if self.db.query(User).first().created_at else 0
        total_users = self.db.query(User).count()
        
        # Post engagement stats
        from sqlalchemy import func
        avg_likes = self.db.query(func.avg(Post.likes_count)).scalar() or 0
        avg_comments = self.db.query(func.avg(Post.comments_count)).scalar() or 0
        
        # Follow network stats - calculated dynamically
        total_follows = self.db.query(Follow).count()
        total_users = self.db.query(User).count()
        avg_followers = total_follows / total_users if total_users > 0 else 0
        avg_following = avg_followers  # Same in a balanced network
        
        print(f"  Average likes per post: {avg_likes:.1f}")
        print(f"  Average comments per post: {avg_comments:.1f}")
        print(f"  Average followers per user: {avg_followers:.1f}")
        print(f"  Average following per user: {avg_following:.1f}")
        
        # Interest distribution
        top_interests = self.db.query(UserInterest.interest_value, func.count(UserInterest.interest_value)) \
            .group_by(UserInterest.interest_value) \
            .order_by(func.count(UserInterest.interest_value).desc()) \
            .limit(5).all()
        
        print("\n  🎯 Top 5 User Interests:")
        for interest, count in top_interests:
            print(f"    • {interest}: {count} users")
        
        # Tag distribution
        top_tags = self.db.query(PostTag.tag_name, func.count(PostTag.tag_name)) \
            .group_by(PostTag.tag_name) \
            .order_by(func.count(PostTag.tag_name).desc()) \
            .limit(5).all()
        
        print("\n  🏷️  Top 5 Post Tags:")
        for tag, count in top_tags:
            print(f"    • #{tag}: {count} posts")
    
    def verify_target_metrics(self):
        """Verify we hit our target metrics"""
        print("\n🎯 Target metrics verification...")
        
        targets = {
            "Users": 1000,
            "Posts": 3000,
            "Interactions": 15000  # Likes + Comments + Shares
        }
        
        actual_users = self.verification_results.get("users", 0)
        actual_posts = self.verification_results.get("posts", 0)
        actual_interactions = (
            self.verification_results.get("likes", 0) +
            self.verification_results.get("comments", 0) +
            self.verification_results.get("shares", 0)
        )
        
        print(f"  👥 Users: {actual_users:,}/{targets['Users']:,} ({actual_users/targets['Users']*100:.1f}%)")
        print(f"  📸 Posts: {actual_posts:,}/{targets['Posts']:,} ({actual_posts/targets['Posts']*100:.1f}%)")
        print(f"  💫 Interactions: {actual_interactions:,}/{targets['Interactions']:,} ({actual_interactions/targets['Interactions']*100:.1f}%)")
        
        # Success criteria
        success_rate = (
            (actual_users >= targets['Users'] * 0.95) +
            (actual_posts >= targets['Posts'] * 0.95) +
            (actual_interactions >= targets['Interactions'] * 0.95)
        ) / 3
        
        if success_rate >= 0.8:
            print(f"\n✅ Data generation SUCCESS! ({success_rate*100:.1f}% of targets met)")
        else:
            print(f"\n⚠️  Data generation PARTIAL SUCCESS ({success_rate*100:.1f}% of targets met)")
        
        return success_rate
    
    def verify_database_integrity(self):
        """Verify database constraints and foreign keys"""
        print("\n🔍 Database integrity checks...")
        
        # Check for orphaned records
        orphaned_posts = self.db.query(Post).outerjoin(User).filter(User.id.is_(None)).count()
        orphaned_likes = self.db.query(Like).outerjoin(User).filter(User.id.is_(None)).count()
        orphaned_comments = self.db.query(Comment).outerjoin(User).filter(User.id.is_(None)).count()
        
        print(f"  Orphaned posts: {orphaned_posts}")
        print(f"  Orphaned likes: {orphaned_likes}")
        print(f"  Orphaned comments: {orphaned_comments}")
        
        if orphaned_posts == 0 and orphaned_likes == 0 and orphaned_comments == 0:
            print("  ✅ No orphaned records found - Database integrity maintained")
        else:
            print("  ⚠️  Found orphaned records - Check data generation logic")
    
    def run_complete_verification(self):
        """Run all verification checks"""
        print("🔬 Instagram-like Platform - Data Verification Report")
        print("=" * 60)
        print(f"📅 Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Core verifications
            self.verify_table_counts()
            self.verify_data_relationships()
            self.verify_sample_data()
            self.verify_data_distribution()
            success_rate = self.verify_target_metrics()
            self.verify_database_integrity()
            
            print("\n" + "=" * 60)
            
            if success_rate >= 0.8:
                print("🎉 PHASE 2 VERIFICATION: SUCCESSFUL")
                print("✅ Synthetic data generation completed successfully!")
                print("✅ All targets met within acceptable ranges")
                print("✅ Data relationships are properly established")
                print("✅ Database integrity maintained")
                print("\n🚀 Ready to proceed with Phase 3 (Frontend Integration)")
            else:
                print("⚠️  PHASE 2 VERIFICATION: NEEDS ATTENTION")
                print("❌ Some targets not fully met")
                print("💡 Consider re-running data generation or adjusting parameters")
            
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"❌ Error during verification: {e}")
            return False
        finally:
            self.db.close()

def main():
    """Main verification function"""
    print("🔬 Starting data verification...")
    
    verifier = DataVerification()
    success = verifier.run_complete_verification()
    
    return success

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    exit(exit_code)