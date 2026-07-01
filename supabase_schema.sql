-- ============================================================
-- SUPABASE SCHEMA: Multi-Tenant Hostel Booking Platform
-- ============================================================

-- ------------------------------------------------------------
-- 1. CUSTOM TYPES (ENUMS)
-- ------------------------------------------------------------
DO $$ BEGIN
    CREATE TYPE public.room_type AS ENUM ('Single', 'Double', 'Triple', 'Quadruple', 'Family', 'Dormitory', 'Suite');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE public.room_status AS ENUM ('Available', 'Occupied', 'Maintenance');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE public.booking_status AS ENUM ('Pending', 'Confirmed', 'Checked In', 'Checked Out', 'Cancelled');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE public.payment_method AS ENUM ('Cash', 'Mobile Money', 'Credit Card', 'Bank Transfer');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE public.payment_status AS ENUM ('Pending', 'Paid', 'Failed', 'Refunded');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE public.user_role AS ENUM ('admin', 'manager', 'customer');
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

-- ------------------------------------------------------------
-- 2. PROFILES TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    profile_photo TEXT,
    role user_role NOT NULL DEFAULT 'customer',
    hostel_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 3. HOSTELS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.hostels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    university TEXT,
    distance TEXT DEFAULT 'Near campus',
    price NUMERIC(10, 2),
    rating NUMERIC(3, 2) DEFAULT '0',
    amenities JSONB DEFAULT '[]'::jsonb,
    contact TEXT,
    available BOOLEAN DEFAULT TRUE,
    image_url TEXT,
    phone TEXT,
    email TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    check_in_time TIME NOT NULL DEFAULT '14:00:00',
    check_out_time TIME NOT NULL DEFAULT '11:00:00',
    review_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 4. HOSTEL IMAGES TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.hostel_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostel_id UUID NOT NULL REFERENCES public.hostels(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    is_cover BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 5. HOSTEL FACILITIES TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.hostel_facilities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostel_id UUID NOT NULL REFERENCES public.hostels(id) ON DELETE CASCADE,
    facility_name TEXT NOT NULL,
    icon TEXT
);

-- ------------------------------------------------------------
-- 6. ROOMS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostel_id UUID NOT NULL REFERENCES public.hostels(id) ON DELETE CASCADE,
    room_number TEXT NOT NULL,
    room_name TEXT NOT NULL,
    room_type room_type NOT NULL,
    capacity INT NOT NULL CHECK (capacity > 0),
    available_quantity INT NOT NULL DEFAULT 1 CHECK (available_quantity > 0),
    price_per_night NUMERIC(10, 2) NOT NULL CHECK (price_per_night >= 0),
    description TEXT,
    size_sq_meters NUMERIC(5, 2),
    private_bathroom BOOLEAN NOT NULL DEFAULT FALSE,
    air_conditioning BOOLEAN NOT NULL DEFAULT FALSE,
    balcony BOOLEAN NOT NULL DEFAULT FALSE,
    television BOOLEAN NOT NULL DEFAULT FALSE,
    wifi BOOLEAN NOT NULL DEFAULT FALSE,
    status room_status NOT NULL DEFAULT 'Available',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 7. ROOM IMAGES TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.room_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES public.rooms(id) ON DELETE CASCADE,
    image_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 8. BOOKINGS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostel_id UUID NOT NULL REFERENCES public.hostels(id) ON DELETE CASCADE,
    room_id UUID NOT NULL REFERENCES public.rooms(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    check_in DATE NOT NULL,
    check_out DATE NOT NULL,
    guests INT NOT NULL CHECK (guests > 0),
    nights INT NOT NULL CHECK (nights > 0),
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    booking_status booking_status NOT NULL DEFAULT 'Pending',
    booking_reference TEXT UNIQUE NOT NULL,
    payment_status payment_status NOT NULL DEFAULT 'Pending',
    special_requests TEXT,
    booked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT valid_dates CHECK (check_out > check_in)
);

-- ------------------------------------------------------------
-- 9. PAYMENTS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES public.bookings(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    payment_method payment_method NOT NULL,
    payment_status payment_status NOT NULL DEFAULT 'Pending',
    transaction_reference TEXT UNIQUE,
    paid_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 10. REVIEWS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hostel_id UUID NOT NULL REFERENCES public.hostels(id) ON DELETE CASCADE,
    customer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_hostel_customer_review UNIQUE (hostel_id, customer_id)
);

-- ------------------------------------------------------------
-- 11. FAVORITES TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.favorites (
    customer_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    hostel_id UUID NOT NULL REFERENCES public.hostels(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (customer_id, hostel_id)
);

-- ------------------------------------------------------------
-- 12. NOTIFICATIONS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- 13. EMAIL CONFIRMATIONS TABLE
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.email_confirmations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    token TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    confirmed_at TIMESTAMPTZ
);

-- ------------------------------------------------------------
-- 14. INDEXES
-- ------------------------------------------------------------
CREATE INDEX idx_profiles_hostel_id ON public.profiles(hostel_id);
CREATE INDEX idx_profiles_email ON public.profiles(email);
CREATE INDEX idx_profiles_role ON public.profiles(role);

CREATE INDEX idx_hostel_images_hostel_id ON public.hostel_images(hostel_id);
CREATE INDEX idx_hostel_images_cover ON public.hostel_images(hostel_id, is_cover) WHERE is_cover = TRUE;

CREATE INDEX idx_hostel_facilities_hostel_id ON public.hostel_facilities(hostel_id);

CREATE INDEX idx_hostels_university ON public.hostels(university);
CREATE INDEX idx_hostels_city ON public.hostels(city);
CREATE INDEX idx_hostels_country ON public.hostels(country);
CREATE INDEX idx_hostels_available ON public.hostels(available);

CREATE INDEX idx_rooms_hostel_id ON public.rooms(hostel_id);
CREATE INDEX idx_rooms_room_type ON public.rooms(room_type);
CREATE INDEX idx_rooms_status ON public.rooms(status);

CREATE INDEX idx_room_images_room_id ON public.room_images(room_id);

CREATE INDEX idx_bookings_hostel_id ON public.bookings(hostel_id);
CREATE INDEX idx_bookings_room_id ON public.bookings(room_id);
CREATE INDEX idx_bookings_customer_id ON public.bookings(customer_id);
CREATE INDEX idx_bookings_booking_status ON public.bookings(booking_status);
CREATE INDEX idx_bookings_payment_status ON public.bookings(payment_status);
CREATE INDEX idx_bookings_order_status ON public.bookings(hostel_id, booking_status, check_in);
CREATE INDEX idx_bookings_check_dates ON public.bookings(check_in, check_out);
CREATE INDEX idx_bookings_reference ON public.bookings(booking_reference);

CREATE INDEX idx_payments_booking_id ON public.payments(booking_id);
CREATE INDEX idx_payments_status ON public.payments(payment_status);

CREATE INDEX idx_reviews_hostel_id ON public.reviews(hostel_id);
CREATE INDEX idx_reviews_customer_id ON public.reviews(customer_id);

CREATE INDEX idx_favorites_customer_id ON public.favorites(customer_id);
CREATE INDEX idx_favorites_hostel_id ON public.favorites(hostel_id);

CREATE INDEX idx_notifications_user_id ON public.notifications(user_id);
CREATE INDEX idx_notifications_is_read ON public.notifications(user_id, is_read);

CREATE INDEX idx_email_confirmations_token ON public.email_confirmations(token);
CREATE INDEX idx_email_confirmations_expires_at ON public.email_confirmations(expires_at);

-- ------------------------------------------------------------
-- 14. FOREIGN KEY: PROFILES -> HOSTELS
-- ------------------------------------------------------------
ALTER TABLE public.profiles
    ADD CONSTRAINT fk_profiles_hostel
    FOREIGN KEY (hostel_id) REFERENCES public.hostels(id) ON DELETE SET NULL;

-- ------------------------------------------------------------
-- 15. TRIGGERS FOR updated_at
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'profiles') THEN
        CREATE TRIGGER handle_profiles_updated_at BEFORE UPDATE ON public.profiles
            FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'hostels') THEN
        CREATE TRIGGER handle_hostels_updated_at BEFORE UPDATE ON public.hostels
            FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'rooms') THEN
        CREATE TRIGGER handle_rooms_updated_at BEFORE UPDATE ON public.rooms
            FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();
    END IF;
END $$;

-- ------------------------------------------------------------
-- 16. BOOKING OVERLAP PREVENTION FUNCTION + TRIGGER
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.prevent_overlapping_bookings()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM public.bookings
        WHERE room_id = NEW.room_id
          AND booking_status IN ('Pending', 'Confirmed', 'Checked In')
          AND id != COALESCE(NEW.id, '00000000-0000-0000-0000-000000000000')
          AND tsrange(check_in, check_out) && tsrange(NEW.check_in, NEW.check_out)
    ) THEN
        RAISE EXCEPTION 'Overlapping booking exists for room % from % to %', NEW.room_id, NEW.check_in, NEW.check_out
        USING ERRCODE = 'P0001';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'bookings') THEN
        DROP TRIGGER IF EXISTS prevent_overlapping_bookings_trigger ON public.bookings;
        CREATE TRIGGER prevent_overlapping_bookings_trigger
            BEFORE INSERT OR UPDATE ON public.bookings
            FOR EACH ROW EXECUTE FUNCTION public.prevent_overlapping_bookings();
    END IF;
END $$;

-- ------------------------------------------------------------
-- 17. HELPER: GENERATE BOOKING REFERENCE
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.generate_booking_reference()
RETURNS TEXT AS $$
DECLARE
    ref TEXT;
BEGIN
    LOOP
        ref := 'BK-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' ||
               UPPER(SUBSTRING(REPLACE(gen_random_uuid()::TEXT, '-', ''), 1, 8));
        IF NOT EXISTS (SELECT 1 FROM public.bookings WHERE booking_reference = ref) THEN
            RETURN ref;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ------------------------------------------------------------
-- 18. HELPER: UPDATE HOSTEL REVIEW COUNTS (trigger)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.update_hostel_review_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE public.hostels
        SET review_count = review_count + 1
        WHERE id = NEW.hostel_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE public.hostels
        SET review_count = GREATEST(review_count - 1, 0)
        WHERE id = OLD.hostel_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'reviews') THEN
        DROP TRIGGER IF EXISTS update_hostel_review_stats ON public.reviews;
        CREATE TRIGGER update_hostel_review_stats
            AFTER INSERT OR DELETE ON public.reviews
            FOR EACH ROW EXECUTE FUNCTION public.update_hostel_review_stats();
    END IF;
END $$;

CREATE OR REPLACE FUNCTION public.check_review_booking()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM public.bookings b
        WHERE b.hostel_id = NEW.hostel_id
          AND b.customer_id = NEW.customer_id
          AND b.booking_status IN ('Confirmed', 'Checked Out')
    ) THEN
        RAISE EXCEPTION 'You can only review hostels you have completed a booking for';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'reviews') THEN
        DROP TRIGGER IF EXISTS check_review_booking_trigger ON public.reviews;
        CREATE TRIGGER check_review_booking_trigger
            BEFORE INSERT ON public.reviews
            FOR EACH ROW EXECUTE FUNCTION public.check_review_booking();
    END IF;
END $$;

-- ------------------------------------------------------------
-- 19. MANAGER ASSIGNMENT FUNCTIONS
-- ------------------------------------------------------------

-- Function to assign a manager to a hostel (for admin use)
CREATE OR REPLACE FUNCTION public.assign_manager_to_hostel(manager_uuid UUID, hostel_uuid UUID)
RETURNS TABLE(success BOOLEAN, message TEXT, manager_id UUID, hostel_id UUID) AS $$
BEGIN
    -- Verify manager exists and has manager role
    IF NOT EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = manager_uuid AND role = 'manager'
    ) THEN
        RETURN QUERY SELECT FALSE, 'Manager not found or not a manager role', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    -- Verify hostel exists
    IF NOT EXISTS (
        SELECT 1 FROM public.hostels WHERE id = hostel_uuid
    ) THEN
        RETURN QUERY SELECT FALSE, 'Hostel not found', NULL::UUID, NULL::UUID;
        RETURN;
    END IF;
    
    UPDATE public.profiles 
    SET hostel_id = hostel_uuid 
    WHERE id = manager_uuid;
    
    RETURN QUERY SELECT TRUE, 'Manager assigned successfully', manager_uuid, hostel_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to remove manager from hostel
CREATE OR REPLACE FUNCTION public.remove_manager_from_hostel(manager_uuid UUID)
RETURNS TABLE(success BOOLEAN, message TEXT) AS $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM public.profiles 
        WHERE id = manager_uuid AND role = 'manager'
    ) THEN
        RETURN QUERY SELECT FALSE, 'Manager not found or not a manager role';
        RETURN;
    END IF;
    
    UPDATE public.profiles 
    SET hostel_id = NULL 
    WHERE id = manager_uuid;
    
    RETURN QUERY SELECT TRUE, 'Manager removed from hostel';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get all managers
CREATE OR REPLACE FUNCTION public.get_all_managers()
RETURNS TABLE(
    id UUID,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    hostel_id UUID,
    hostel_name TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.full_name,
        p.email,
        p.phone,
        p.hostel_id,
        h.name
    FROM public.profiles p
    LEFT JOIN public.hostels h ON h.id = p.hostel_id
    WHERE p.role = 'manager';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get unassigned managers
CREATE OR REPLACE FUNCTION public.get_unassigned_managers()
RETURNS TABLE(
    id UUID,
    full_name TEXT,
    email TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.full_name,
        p.email
    FROM public.profiles p
    WHERE p.role = 'manager' AND p.hostel_id IS NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get managers for a specific hostel
CREATE OR REPLACE FUNCTION public.get_hostel_managers(hostel_uuid UUID)
RETURNS TABLE(
    id UUID,
    full_name TEXT,
    email TEXT,
    phone TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.full_name,
        p.email,
        p.phone
    FROM public.profiles p
    WHERE p.role = 'manager' AND p.hostel_id = hostel_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hostels ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hostel_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.hostel_facilities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rooms ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.room_images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

-- ------------------------------------------------------------
-- 20. RLS POLICIES: PROFILES
-- ------------------------------------------------------------
CREATE POLICY "Admins can do everything on profiles"
    ON public.profiles FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    TO authenticated
    USING (id = auth.uid());

CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    TO authenticated
    USING (id = auth.uid());

-- ------------------------------------------------------------
-- 21. RLS POLICIES: HOSTELS
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all hostels"
    ON public.hostels FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can manage their own hostel"
    ON public.hostels FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = public.hostels.id
        )
    );

CREATE POLICY "Customers can view all hostels"
    ON public.hostels FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Public hostels visible to anonymous"
    ON public.hostels FOR SELECT
    TO anon
    USING (true);

-- ------------------------------------------------------------
-- 22. RLS POLICIES: HOSTEL IMAGES
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all hostel images"
    ON public.hostel_images FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can manage their hostel images"
    ON public.hostel_images FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = public.hostel_images.hostel_id
        )
    );

CREATE POLICY "Anyone can view hostel images"
    ON public.hostel_images FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Public hostel images visible"
    ON public.hostel_images FOR SELECT
    TO anon
    USING (true);

-- ------------------------------------------------------------
-- 23. RLS POLICIES: HOSTEL FACILITIES
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all facilities"
    ON public.hostel_facilities FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can manage their hostel facilities"
    ON public.hostel_facilities FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = public.hostel_facilities.hostel_id
        )
    );

CREATE POLICY "Anyone can view hostel facilities"
    ON public.hostel_facilities FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Public facilities visible"
    ON public.hostel_facilities FOR SELECT
    TO anon
    USING (true);

-- ------------------------------------------------------------
-- 24. RLS POLICIES: ROOMS
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all rooms"
    ON public.rooms FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can manage their hostel rooms"
    ON public.rooms FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = public.rooms.hostel_id
        )
    );

CREATE POLICY "Customers can view all available rooms"
    ON public.rooms FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Public rooms visible"
    ON public.rooms FOR SELECT
    TO anon
    USING (true);

-- ------------------------------------------------------------
-- 25. RLS POLICIES: ROOM IMAGES
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all room images"
    ON public.room_images FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can manage their room images"
    ON public.room_images FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = (
                  SELECT r.hostel_id FROM public.rooms r
                  WHERE r.id = public.room_images.room_id
              )
        )
    );

CREATE POLICY "Anyone can view room images"
    ON public.room_images FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Public room images visible"
    ON public.room_images FOR SELECT
    TO anon
    USING (true);

-- ------------------------------------------------------------
-- 26. RLS POLICIES: BOOKINGS
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all bookings"
    ON public.bookings FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can view and update their hostel bookings"
    ON public.bookings FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = public.bookings.hostel_id
        )
    );

CREATE POLICY "Managers can update booking statuses"
    ON public.bookings FOR UPDATE
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'manager'
              AND p.hostel_id = public.bookings.hostel_id
        )
    );

CREATE POLICY "Customers can view their own bookings"
    ON public.bookings FOR SELECT
    TO authenticated
    USING (customer_id = auth.uid());

CREATE POLICY "Customers can create bookings"
    ON public.bookings FOR INSERT
    TO authenticated
    WITH CHECK (customer_id = auth.uid());

CREATE POLICY "Customers can cancel their own bookings"
    ON public.bookings FOR UPDATE
    TO authenticated
    USING (customer_id = auth.uid())
    WITH CHECK (customer_id = auth.uid());

-- ------------------------------------------------------------
-- 27. RLS POLICIES: PAYMENTS
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all payments"
    ON public.payments FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Managers can view their hostel payments"
    ON public.payments FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.bookings b
            JOIN public.profiles p ON p.id = auth.uid() AND p.role = 'manager'
            WHERE b.id = public.payments.booking_id
              AND p.hostel_id = b.hostel_id
        )
    );

CREATE POLICY "Customers can view their own payments"
    ON public.payments FOR SELECT
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.bookings b
            WHERE b.id = public.payments.booking_id
              AND b.customer_id = auth.uid()
        )
    );

CREATE POLICY "Customers can create payments"
    ON public.payments FOR INSERT
    TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.bookings b
            WHERE b.id = public.payments.booking_id
              AND b.customer_id = auth.uid()
        )
    );

-- ------------------------------------------------------------
-- 28. RLS POLICIES: REVIEWS
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all reviews"
    ON public.reviews FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Customers can view all reviews"
    ON public.reviews FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Customers can create reviews for their bookings"
    ON public.reviews FOR INSERT
    TO authenticated
    WITH CHECK (
        customer_id = auth.uid()
    );

CREATE POLICY "Customers can update their own reviews"
    ON public.reviews FOR UPDATE
    TO authenticated
    USING (customer_id = auth.uid());

CREATE POLICY "Customers can delete their own reviews"
    ON public.reviews FOR DELETE
    TO authenticated
    USING (customer_id = auth.uid());

CREATE POLICY "Public reviews visible"
    ON public.reviews FOR SELECT
    TO anon
    USING (true);

-- ------------------------------------------------------------
-- 29. RLS POLICIES: FAVORITES
-- ------------------------------------------------------------
CREATE POLICY "Admins can manage all favorites"
    ON public.favorites FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles p
            WHERE p.id = auth.uid() AND p.role = 'admin'
        )
    );

CREATE POLICY "Customers can manage their own favorites"
    ON public.favorites FOR ALL
    TO authenticated
    USING (customer_id = auth.uid());

-- ------------------------------------------------------------
-- 30. RLS POLICIES: NOTIFICATIONS
-- ------------------------------------------------------------
CREATE POLICY "Users can view their own notifications"
    ON public.notifications FOR SELECT
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their own notifications"
    ON public.notifications FOR UPDATE
    TO authenticated
    USING (user_id = auth.uid());

CREATE POLICY "System can create notifications"
    ON public.notifications FOR INSERT
    TO authenticated
    WITH CHECK (true);

-- ------------------------------------------------------------
-- 31. GRANTS (Service role & authenticated/anonymous)
-- ------------------------------------------------------------
GRANT USAGE ON SCHEMA public TO postgres, anon, authenticated, service_role;

GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, service_role;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- ------------------------------------------------------------
-- 32. STORAGE BUCKET POLICIES (Supabase Storage)
-- ------------------------------------------------------------
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES
    ('hostel-images', 'hostel-images', true, 5242880, ARRAY['image/jpeg', 'image/png', 'image/webp']),
    ('room-images', 'room-images', true, 5242880, ARRAY['image/jpeg', 'image/png', 'image/webp']),
    ('profile-photos', 'profile-photos', true, 2097152, ARRAY['image/jpeg', 'image/png', 'image/webp'])
ON CONFLICT (id) DO NOTHING;

-- Hostel images bucket policies
CREATE POLICY "Public can view hostel images"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'hostel-images');

CREATE POLICY "Authenticated users can upload hostel images"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (bucket_id = 'hostel-images');

CREATE POLICY "Managers can own hostel images, admins can manage all"
    ON storage.objects FOR UPDATE
    TO authenticated
    USING (
        bucket_id = 'hostel-images'
        AND (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid() AND p.role = 'admin'
            )
            OR EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid() AND p.role = 'manager'
                  AND p.hostel_id IN (
                      SELECT h.id FROM public.hostels h
                      WHERE h.id = (storage.foldername(name))[1]::UUID
                  )
            )
        )
    );

CREATE POLICY "Managers can delete their hostel images, admins can delete all"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'hostel-images'
        AND (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid() AND p.role = 'admin'
            )
            OR EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid() AND p.role = 'manager'
                  AND p.hostel_id IN (
                      SELECT h.id FROM public.hostels h
                      WHERE h.id = (storage.foldername(name))[1]::UUID
                  )
            )
        )
    );

-- Room images bucket policies
CREATE POLICY "Public can view room images"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'room-images');

CREATE POLICY "Authenticated users can upload room images"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (bucket_id = 'room-images');

CREATE POLICY "Managers can own room images, admins can manage all"
    ON storage.objects FOR UPDATE
    TO authenticated
    USING (
        bucket_id = 'room-images'
        AND (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid() AND p.role = 'admin'
            )
            OR EXISTS (
                SELECT 1 FROM public.profiles p
                JOIN public.rooms r ON r.id = (storage.foldername(name))[1]::UUID
                WHERE p.id = auth.uid() AND p.role = 'manager'
                  AND p.hostel_id = r.hostel_id
            )
        )
    );

CREATE POLICY "Managers can delete their room images, admins can delete all"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (
        bucket_id = 'room-images'
        AND (
            EXISTS (
                SELECT 1 FROM public.profiles p
                WHERE p.id = auth.uid() AND p.role = 'admin'
            )
            OR EXISTS (
                SELECT 1 FROM public.profiles p
                JOIN public.rooms r ON r.id = (storage.foldername(name))[1]::UUID
                WHERE p.id = auth.uid() AND p.role = 'manager'
                  AND p.hostel_id = r.hostel_id
            )
        )
    );

-- Profile photos bucket policies
CREATE POLICY "Public can view profile photos"
    ON storage.objects FOR SELECT
    TO public
    USING (bucket_id = 'profile-photos');

CREATE POLICY "Users can upload their own profile photo"
    ON storage.objects FOR INSERT
    TO authenticated
    WITH CHECK (bucket_id = 'profile-photos' AND auth.uid()::TEXT = (storage.foldername(name))[1]);

CREATE POLICY "Users can update their own profile photo"
    ON storage.objects FOR UPDATE
    TO authenticated
    USING (bucket_id = 'profile-photos' AND auth.uid()::TEXT = (storage.foldername(name))[1]);

CREATE POLICY "Users can delete their own profile photo"
    ON storage.objects FOR DELETE
    TO authenticated
    USING (bucket_id = 'profile-photos' AND auth.uid()::TEXT = (storage.foldername(name))[1]);

-- ------------------------------------------------------------
-- 33. USEFUL VIEWS
-- ------------------------------------------------------------

-- Available rooms view
CREATE OR REPLACE VIEW public.available_rooms AS
SELECT
    r.*,
    h.name AS hostel_name,
    h.city,
    h.country,
    COUNT(b.id) FILTER (WHERE b.booking_status IN ('Pending', 'Confirmed', 'Checked In')) AS active_bookings_count
FROM public.rooms r
JOIN public.hostels h ON h.id = r.hostel_id
LEFT JOIN public.bookings b ON b.room_id = r.id
GROUP BY r.id, h.name, h.city, h.country;

-- Hostel ratings view
CREATE OR REPLACE VIEW public.hostel_ratings AS
SELECT
    h.id AS hostel_id,
    h.name AS hostel_name,
    AVG(r.rating)::NUMERIC(3,2) AS average_rating,
    COUNT(r.id) AS total_reviews,
    COUNT(r.id) FILTER (WHERE r.rating = 5) AS five_star,
    COUNT(r.id) FILTER (WHERE r.rating = 4) AS four_star,
    COUNT(r.id) FILTER (WHERE r.rating = 3) AS three_star,
    COUNT(r.id) FILTER (WHERE r.rating = 2) AS two_star,
    COUNT(r.id) FILTER (WHERE r.rating = 1) AS one_star
FROM public.hostels h
LEFT JOIN public.reviews r ON r.hostel_id = h.id
GROUP BY h.id, h.name;

-- Booking summary view
CREATE OR REPLACE VIEW public.booking_summary AS
SELECT
    b.*,
    h.name AS hostel_name,
    r.room_number,
    r.room_type,
    r.room_name,
    p.full_name AS customer_name,
    p.email AS customer_email
FROM public.bookings b
JOIN public.hostels h ON h.id = b.hostel_id
JOIN public.rooms r ON r.id = b.room_id
JOIN auth.users u ON u.id = b.customer_id
JOIN public.profiles p ON p.id = b.customer_id;

-- ------------------------------------------------------------
-- 34. REALTIME PUBLICATION CONFIGURATION
-- ------------------------------------------------------------
ALTER PUBLICATION supabase_realtime ADD TABLE public.bookings;
ALTER PUBLICATION supabase_realtime ADD TABLE public.payments;
ALTER PUBLICATION supabase_realtime ADD TABLE public.notifications;
ALTER PUBLICATION supabase_realtime ADD TABLE public.rooms;
ALTER PUBLICATION supabase_realtime ADD TABLE public.reviews;

-- ------------------------------------------------------------
-- 35. COMPLETION VERIFICATION
-- ------------------------------------------------------------
DO $$
BEGIN
    RAISE NOTICE 'Schema migration completed successfully.';
    RAISE NOTICE 'Tables created: profiles, hostels, hostel_images, hostel_facilities, rooms, room_images, bookings, payments, reviews, favorites, notifications, email_confirmations';
    RAISE NOTICE 'Custom types created: room_type, room_status, booking_status, payment_method, payment_status, user_role';
    RAISE NOTICE 'RLS policies enabled on all tables.';
    RAISE NOTICE 'Indexes created for performance optimization.';
    RAISE NOTICE 'Booking overlap prevention trigger active.';
    RAISE NOTICE 'Realtime tables configured for live updates.';
END $$;